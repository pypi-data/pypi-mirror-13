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
#include <cstdio>
#include <cmath>
#include <queue>
#include <cassert>
#include <algorithm>
#include "gurobi_c.h"
#include "gurobi_c++.h"
#include "common.hpp"
#include "instance.hpp"
#include "arcflow.hpp"
#include "arcflowsol.hpp"
using namespace std;


class GrbArcflow: public Arcflow{
public:
    GrbArcflow(const Instance &inst): Arcflow(inst){}

    void solve(
            const Instance &inst, bool print_inst = false, bool pyout = false){
        assert(ready == true);
        char vtype = inst.vtype;
        GRBEnv* env = new GRBEnv();
        GRBModel model = GRBModel(*env);
        model.set(GRB_StringAttr_ModelName, "flow");

        model.getEnv().set(GRB_IntParam_OutputFlag, 1);
        model.getEnv().set(GRB_IntParam_Threads, 1);
        model.getEnv().set(GRB_IntParam_Presolve, 1);
        //model.getEnv().set(GRB_IntParam_Method, 0);
        model.getEnv().set(GRB_IntParam_Method, 2);
        model.getEnv().set(GRB_IntParam_MIPFocus, 1);
        //model.getEnv().set(GRB_IntParam_RINS, 1);
        model.getEnv().set(GRB_DoubleParam_Heuristics, 1);
        model.getEnv().set(GRB_DoubleParam_MIPGap, 0);
        model.getEnv().set(GRB_DoubleParam_MIPGapAbs, 1-1e-5);
        //model.getEnv().set(GRB_DoubleParam_ImproveStartTime, 60);
        //model.getEnv().set(GRB_DoubleParam_ImproveStartGap, 1);

        sort(All(A));
        //reverse(All(A));
        map<Arc, GRBVar> va;
        int lastv = Ts[0]-1;
        for(int i = 0; i < inst.nbtypes; i++) lastv = min(lastv, Ts[i]-1);
        for(int i = 0; i < 3; i++){
            ForEach(a, A){
                if(i == 1 && a->u != S) continue;
                if(i == 2 && a->v <= lastv) continue;
                if(i == 0 && (a->u == S || a->v > lastv)) continue;

                if(a->label == LOSS || inst.relax_domains)
                    va[*a] = model.addVar(0.0, inst.n, 0, vtype);
                else
                    va[*a] = model.addVar(0.0, items[a->label].demand, 0, vtype);
            }
        }
        model.update();

        for(int i = 0; i < inst.nbtypes; i++){
            GRBVar &feedback = va[Arc(Ts[i], S, LOSS)];
            feedback.set(GRB_DoubleAttr_Obj, inst.Cs[i]);
            if(inst.Qs[i] >= 0)
                feedback.set(GRB_DoubleAttr_UB, inst.Qs[i]);
        }

        vector<vector<Arc> > Al(nsizes);
        vector<vector<Arc> > in(NS.size()+Ts.size());
        vector<vector<Arc> > out(NS.size()+Ts.size());

        ForEach(itr, A){
            if(itr->label != LOSS)
                Al[itr->label].push_back(*itr);
            out[itr->u].push_back(*itr);
            in[itr->v].push_back(*itr);
        }

        for(int i = 0; i < inst.m; i++){
            GRBLinExpr lin = 0;
            for(int it = 0; it < nsizes; it++)
                if(items[it].type == i) ForEach(a, Al[it]) lin += va[*a];
            if(inst.ctypes[i] == '>' || inst.relax_domains)
                model.addConstr(lin >= inst.demands[i]);
            else
                model.addConstr(lin == inst.demands[i]);
        }

        for(int u = 0; u < NS.size()+nbtypes; u++){
            GRBLinExpr lin = 0;
            ForEach(a, in[u]) lin += va[*a];
            ForEach(a, out[u]) lin -= va[*a];
            model.addConstr(lin == 0);
        }

        Al.clear();
        in.clear();
        out.clear();

        double pre = TIMEDIF(tstart);
        model.optimize();
        printf("Preprocessing time: %.2f seconds\n", pre);
        double tg = model.get(GRB_DoubleAttr_Runtime);
        printf("Gurobi run time: %.2f seconds\n", tg);
        printf("Total run time: %.2f seconds\n", tg+pre);

        if(inst.vtype == 'I'){
            map<Arc, int> flow;
            ForEach(a, va){
                double x = a->second.get(GRB_DoubleAttr_X);
                int rx = (int)round(x);
                assert(x - rx <= EPS);
                if(rx > 0){
                    int u = a->first.u;
                    int v = a->first.v;
                    int lbl = a->first.label;
                    Arc a(u, v, lbl);
                    flow[a] = rx;
                }
            }
            ArcflowSol sol(inst, flow, S, Ts, LOSS, binary);
            sol.print_solution(inst, print_inst, pyout, true);
        }

        free(env);
    }
};

int main(int argc, char *argv[]){
    printf("Copyright (C) 2013-2016, Filipe Brandao\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc < 2 || argc > 7){
        printf("Usage: vpsolver instance.vbp/instance.mvp "
               "[method:-2] [binary:0] [vtype:I] "
               "[print_instance:0] [pyout:0]\n");
        return 1;
    }

    Instance inst(argv[1]);
    if(argc >= 3) {
        inst.method = atoi(argv[2]);
        assert(inst.method >= MIN_METHOD && inst.method <= MAX_METHOD);
    }
    if(argc >= 4){
        inst.binary = atoi(argv[3]);
    }
    if(argc >= 5){
        inst.vtype = argv[4][0];
        assert(inst.vtype == 'I' || inst.vtype == 'C');
    }
    bool print_inst = false;
    if(argc >= 6){
        print_inst = atoi(argv[5]) != 0;
    }
    bool pyout = false;
    if(argc >= 7){
        pyout = atoi(argv[6]) != 0;
    }

    try {
        GrbArcflow graph(inst);
        graph.solve(inst, print_inst, pyout);
    } catch(GRBException e) {
        printf("Error code = %d\n", e.getErrorCode());
        printf("%s\n", e.getMessage().c_str());
    } catch (...) {
        printf("Error during optimization\n");
    }
    return 0;
}
