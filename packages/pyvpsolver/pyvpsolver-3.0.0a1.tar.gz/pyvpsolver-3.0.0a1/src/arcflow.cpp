/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
**/
#include <set>
#include <climits>
#include <cstring>
#include <cassert>
#include <ctime>
#include <bitset>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
#include "arcflow.hpp"
using namespace std;

/* Class Arcflow */

Arcflow::Arcflow(const Instance &inst){
    tstart = CURTIME;
    ready = false;
    nsizes = inst.nsizes;
    LOSS = inst.nsizes;
    nbtypes = inst.nbtypes;
    Ws = inst.Ws;
    ndims = inst.ndims;
    items = inst.items;
    binary = inst.binary;
    int method = inst.method;

    maxW.resize(ndims, 0);
    for(int d = 0; d < ndims; d++){
        for(int t = 0; t < nbtypes; t++)
            maxW[d] = max(maxW[d], Ws[t][d]);
    }

    lsize = ndims;
    max_label = maxW;
    if(binary){
        lsize = ndims+1;
        max_label.push_back(INT_MAX);
    }

    Item loss(ndims);
    for(int d = 0; d < ndims; d++)
        loss[d] = 0;
    loss.demand = INT_MAX;
    items.push_back(loss);

    printf("Build (method = %d)\n", method);
    assert(method >= MIN_METHOD && method <= MAX_METHOD);

    build(); // build step-3' graph
    int nv1 = NS.size()+nbtypes;
    int na1 = A.size()+(NS.size()-1)*nbtypes+1;
    printf("  Step-3' Graph: %d vertices and %d arcs (%.2fs)\n",
        nv1, na1, TIMEDIF(tstart));

    final_compression_step(); // create step-4' graph
    finalize(); // add the final loss arcs
    int nv2 = NS.size()+Ts.size();
    int na2 = A.size();
    printf("  Step-4' Graph: %d vertices and %d arcs (%.2fs)\n",
        nv2, na2, TIMEDIF(tstart));
    printf("  #V4/#V3 = %.2f\n", nv2/double(nv1));
    printf("  #A4/#A3 = %.2f\n", na2/double(na1));
    printf("Ready! (%.2fs)\n", TIMEDIF(tstart));
}

bool Arcflow::is_valid(const vector<int> &u, const vector<int> &W) const{
    for(int i = 0; i < ndims; i++)
        if(u[i] > W[i]) return false;
    return true;
}

bool Arcflow::is_full(const vector<int> &u, const vector<int> &W) const{
    for(int i = 0; i < ndims; i++)
        if(u[i] != W[i]) return false;
    return true;
}

void Arcflow::relabel_graph(const vector<int> &label){
    set<Arc> arcs;
    ForEach(itr, A){
        int u = label[itr->u];
        int v = label[itr->v];
        if(u != v)
            arcs.insert(Arc(u, v, itr->label));
    }
    A.assign(All(arcs));
}

vector<int> Arcflow::max_rep(
        const vector<int> &W, const vector<int> &u,
        int i0 = 0, int sub_i0 = 0) const {
    vector<int> r(nsizes);
    for(int i = i0; i < nsizes; i++){
        int dem = binary ? 1 : items[i].demand;
        if(i != i0)
            r[i] = dem;
        else
            r[i] = max(0, dem-sub_i0);
        for(int d = 0; d < ndims && r[i] > 0; d++)
            if(items[i][d] != 0)
                r[i] = min(r[i], (W[d]-u[d])/items[i][d]);
    }
    return r;
}

int Arcflow::min_slack(const vector<int> &b, int i0, int d, const vector<int> &caps) const {
    int C = caps.back();
    if(C == 0) return 0;
    vector<int> Q;
    bool vis[C+1];
    memset(&vis, 0, sizeof(vis));
    vis[0] = true;
    Q.push_back(0);
    int res = 0;
    for(int i = i0; i < nsizes; i++){
        int w = items[i][d];
        int qs = Q.size();
        for(int j = 0; j < qs; j++){
            int u = Q[j];
            int v = u;
            for(int k = 1; k <= b[i]; k++){
                v += w;
                if(v > C) break;
                if(v == C) return 0;
                if(vis[v]) break;
                res = max(res, v);
                Q.push_back(v);
            }
        }
        for(int j = qs; j < (int)Q.size(); j++)
            vis[Q[j]] = true;
    }
    if(res <= caps[0]){
        return caps[0]-res;
    }else{
        int mslack = C-res;
        for(int cap: caps){
            int p = cap;
            while(!vis[p] && cap-p <= mslack) p--;
            mslack = min(mslack, cap-p);
        }
        return mslack;
    }
}

void Arcflow::lift_state(
        const vector<int> &valid_opts, vector<int> &u, int it, int ic) const {
    if(it >= nsizes) return;
    const vector<int> &r = max_rep(maxW, u, it, ic);
    for(int d = 0; d < ndims; d++){
        int minw = maxW[d];
        for(int t : valid_opts) minw = min(minw, Ws[t][d]);
        if(u[d] != minw){
            // lift method 1
            int maxpos = minw;
            for(int i = it; i < nsizes && maxpos >= u[d]; i++)
                maxpos -= r[i]*items[i][d];
            if(maxpos >= u[d]){
                u[d] = maxpos;
            }else{
                // lift method 2
                vector<int> caps;
                for(int t : valid_opts)
                    caps.push_back(Ws[t][d]-u[d]);
                if(caps.size() > 1){
                    sort(All(caps));
                    caps.erase(unique(All(caps)), caps.end());
                }
                u[d] += min_slack(r, it, d, caps);
            }
        }
    }
}

inline vector<int> Arcflow::hash(const vector<int> &su){
    if(ndims <= 1) return su;
    static size_t last_size = 1;
    vector<int> h(0);
    h.reserve(last_size);
    int *p = NULL, bits = 0;
    const int all = sizeof(int)*8;
    for(int d = 0; d < ndims; d++){
        int x = su[d], xl = maxW[d];
        while(xl != 0){
            if(bits == 0){
                h.push_back(0);
                p = &h.back();
                bits = all;
            }
            *p = (*p<<1)|(x&1);
            bits--;
            x >>= 1;
            xl >>= 1;
        }
    }
    for(int d = ndims; d < (int)su.size(); d++){
        h.push_back(su[d]);
    }
    last_size = h.size();
    return h;
}

int Arcflow::go(vector<int> su){
    int it = su[ndims];
    int ic = binary ? 0 : su[ndims+1];
    vector<int> valid_opts;
    vector<int> mu(max_label);
    vector<int> maxw(ndims, 0);
    for(int t = 0; t < nbtypes; t++){
        if(is_valid(su, Ws[t])){
            valid_opts.push_back(t);
            for(int d = 0; d < ndims; d++){
                mu[d] = min(mu[d], Ws[t][d]);
                maxw[d] = max(maxw[d], Ws[t][d]);
            }
        }
    }
    if(valid_opts.empty()) // if invalid
        return -1;
    else if(is_full(su, maxw)) // if full
        return NS.get_index(mu);
    else
        lift_state(valid_opts, su, it, ic);

    //const vector<int> key(su);
    const vector<int> key(hash(su));
    map<vector<int>, int>::iterator itr = dp.find(key);
    if(itr != dp.end())
        return itr->second;

    int up = -1;
    if(it+1 < nsizes){
        vector<int> sv(su);
        sv[ndims] = it+1;
        if(!binary)
            sv[ndims+1] = 0;
        up = go(sv);
        assert(up != -1);
        mu = NS.get_label(up);
    }

    int dem = items[it].demand;
    if(it < nsizes && ic < dem){
        vector<int> sv(su);
        const vector<int> &w = items[it].w;
        for(int d = 0; d < ndims; d++){
            sv[d] += w[d];
            if(sv[d] > maxw[d]) // if invalid
                return dp[key] = NS.get_index(mu);
        }

        if(binary){
            sv[ndims] = it+1;
        }else{
            if(ic+1 < dem){
                sv[ndims] = it;
                sv[ndims+1] = ic+1;
            }else{
                sv[ndims] = it+1;
                sv[ndims+1] = 0;
            }
        }
        int iv = go(sv);

        if(iv != -1){
            const vector<int> &v = NS.get_label(iv);
            for(int d = 0; d < ndims; d++)
                mu[d] = min(mu[d], v[d]-w[d]);
            if(binary)
                mu[ndims] = min(mu[ndims], it+1);
            int iu = NS.get_index(mu);
            AS.insert(Arc(iu, iv, it));
            if(up != -1 && iu != up)
                AS.insert(Arc(iu, up, LOSS));
        }
    }

    return dp[key] = NS.get_index(mu);
}

void Arcflow::build(){
    dp.clear();
    A.clear();
    NS.clear();

    if(binary)
        go(vector<int>(lsize, 0));
    else
        go(vector<int>(lsize+2, 0));

    printf("  #dp: %d\n", (int)dp.size());

    dp.clear();
    A.assign(All(AS));
    AS.clear();

    relabel_graph(NS.topological_order());
    NS.sort();
}

void Arcflow::final_compression_step(){
    assert(ready == false);
    int nv = NS.size();
    vector<int> label(nv);
    vector<vector<int_pair> > adj = get_adj(nv, A, TRANSPOSE);

    NodeSet NStmp;
    for(int u = 0; u < NS.size(); u++){
        vector<int> lbl(lsize, 0);
        ForEach(itr, adj[u]){
            assert(itr->first < u);
            int v = label[itr->first];
            int it = itr->second;
            const vector<int> &lv = NStmp.get_label(v);
            for(int d = 0; d < ndims; d++)
                lbl[d] = max(lbl[d], lv[d]+items[it][d]);
            if(binary){
                if(it == LOSS)
                    lbl[ndims] = max(lbl[ndims], lv[ndims]);
                else
                    lbl[ndims] = max(lbl[ndims], max(lv[ndims], it));
            }
        }
        label[u] = NStmp.get_index(lbl);
    }

    NS = NStmp;
    vector<int> order = NS.topological_order();
    ForEach(itr, label)
        *itr = order[*itr];
    relabel_graph(label);
    NS.sort();
}

void Arcflow::reduce_redundancy(){
    //remove redundant parallel arcs
    vector<int> types;
    for(int i = 0; i < nsizes; i++)
        types.push_back(items[i].type);
    types.push_back(-1);
    auto comp_less = [&types](const Arc &a, const Arc &b) {
        return (a.u < b.u) ||
               (a.u == b.u && a.v < b.v) ||
               (a.u == b.u && a.v == b.v && types[a.label] < types[b.label]);
    };
    auto comp_equal = [&types](const Arc &a, const Arc &b) {
        return a.u == b.u && a.v == b.v && types[a.label] == types[b.label];
    };
    sort(All(A), comp_less);
    A.erase(unique(All(A), comp_equal), A.end());
}

void Arcflow::finalize(){
    assert(ready == false);
    if(nbtypes == 1){
        S = 0;
        Ts.assign({NS.size()});
        A.push_back(Arc(Ts[0], S, LOSS));
        for(int i = 1; i < (int)NS.size(); i++)
        A.push_back(Arc(i, Ts[0], LOSS));
    }else{
        S = 0;
        Ts.clear();
        for(int i = 0; i < nbtypes; i++)
            Ts.push_back(i);
        sort(All(Ts), [this](int a, int b) {
            return this->Ws[a] < this->Ws[b];
        });
        for(int i = 0; i < nbtypes; i++)
            Ts[i] += NS.size();

        for(int i = 0; i < nbtypes; i++)
            A.push_back(Arc(Ts[i], S, LOSS));

        vector<vector<int> > bigger_than(nbtypes);
        for(int t1 = 0; t1 < nbtypes; t1++)
            for(int t2 = 0; t2 < nbtypes; t2++)
                if(t1 != t2 && is_valid(Ws[t1], Ws[t2]))
                    if(Ws[t1] != Ws[t2] || (t1 < t2 && Ws[t1] == Ws[t2]))
                        bigger_than[t1].push_back(t2);

        vector<bool> valid_tgts(nbtypes);
        for(int i = 1; i < (int)NS.size(); i++){
            const vector<int> &u = NS.get_label(i);
            for(int t = 0; t < nbtypes; t++)
                valid_tgts[t] = is_valid(u, Ws[t]);
            for(int t1 = 0; t1 < nbtypes; t1++)
                if(valid_tgts[t1])
                    for(int t2 : bigger_than[t1]) valid_tgts[t2] = false;
            for(int t = 0; t < nbtypes; t++)
                if(valid_tgts[t])
                    A.push_back(Arc(i, Ts[t], LOSS));
        }

        for(int t1 = 0; t1 < nbtypes; t1++){
            valid_tgts.assign(nbtypes, false);
            for(int t2 : bigger_than[t1])
                valid_tgts[t2] = true;
            for(int t2 : bigger_than[t1])
                if(valid_tgts[t2])
                    for(int t3 : bigger_than[t2])
                        valid_tgts[t3] = false;
            for(int t2 : bigger_than[t1])
                if(valid_tgts[t2])
                    A.push_back(Arc(Ts[t1], Ts[t2], LOSS));
        }
    }
    reduce_redundancy();
    ready = true;
}

void Arcflow::write(FILE *fout){
    assert(ready == true);
    sort(All(A));

    int iS = 0;
    fprintf(fout, "S: %d\n", iS);
    fprintf(fout, "Ts:");
    for(int t = 0; t < (int)Ts.size(); t++){
        fprintf(fout, " %d", Ts[t]);
    }
    fprintf(fout, "\n");

    fprintf(fout, "LOSS: %d\n", LOSS);

    int lastv = NS.size()-1;
    fprintf(fout, "NV: %d\n", int(NS.size()+Ts.size()));
    fprintf(fout, "NA: %d\n", int(A.size()));

    sort(All(A));
    for(int i = 0; i < 3; i++){
        ForEach(a, A){
            if(i == 1 && a->u != iS) continue;
            if(i == 2 && a->v <= lastv) continue;
            if(i == 0 && (a->u == iS || a->v > lastv)) continue;
            fprintf(fout, "%d %d %d\n", a->u, a->v, a->label);
        }
    }
}

void Arcflow::write(const char *fname){
    FILE *fout = fopen(fname, "w");
    assert(fout != NULL);
    write(fout);
    fclose(fout);
}
