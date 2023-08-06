#-------------------------------------------------------------------------------
# Name:        mypulp.py
# Purpose:     Calling pulp module using the same syntax as in Gurobi
#
# Author:      Mikio Kubo
#
# Created:     21/05/2013
# Copyright:   (c)  Mikio Kubo 2013, 2014, 2015
#-------------------------------------------------------------------------------

from pulp import *
import copy
import math

class GRB():
    class Status:
        pass
    Status.OPTIMAL=1
    Status.INFEASIBLE=3
    Status.INF_OR_UNBD=4
    Status.UNBOUNDED =5
    Status.UNDEFINED =None
    pass

GRB.CONTINUOUS="C"
GRB.INTEGER="I"
GRB.BINARY="B"
GRB.SEMICONT="S"
GRB.SEMIINT ="N"

GRB.MINIMIZE=1
GRB.MAXIMIZE=-1
GRB.INFINITY=1e+100
GRB.MAXINT = 2147483647

GRB.SOS_TYPE1 =1
GRB.SOS_TYPE2 =2

quicksum=lpSum

if int(sys.version_info[0])<=2:
    def gray(i):
        return i^i/2
else:
    def gray(i):
        return i^i//2

def convex_comb_agg_log(model,var_list=[]):
    """convex_comb_agg_log -- add piecewise relation with a logarithmic number of binary variables
    using the convex combination formulation -- non-disaggregated.
    Parameters:
        - model: a model where to include the SOS type 2
        - vars : list of variables that declare the SOS type 2
    """
    K = len(var_list)-1
    G = int(math.ceil((math.log(K)/math.log(2))))     # number of required bits
    g = {}
    for j in range(G):
        g[j] = model.addVar(vtype="B")
    model.addConstr(quicksum(var_list[k] for k in range(K+1)) == 1)
    # binary variables setup
    for j in range(G):
        zeros,ones = [0],[]
        # print j,"\tinit zeros:",zeros,"ones:",ones
        for k in range(1,K+1):
            # print j,k,"\t>zeros:",zeros,"ones:",ones
            if (1 & gray(k)>>j) == 1 and (1 & gray(k-1)>>j) == 1:
                ones.append(k)
            if (1 & gray(k)>>j) == 0 and (1 & gray(k-1)>>j) == 0:
                zeros.append(k)
            # print j,k,"\tzeros>:",zeros,"ones:",ones

        # print j,"\tzeros:",zeros,"ones:",ones
        model.addConstr(quicksum(var_list[k] for k in ones) <= g[j])
        model.addConstr(quicksum(var_list[k] for k in zeros) <= 1-g[j])
    return

def mult_selection(model,x,a,b):
    """mult_selection -- add piecewise relation with multiple selection formulation
    Parameters:
        - model: a model where to include the piecewise linear relation
        - a[k]: x-coordinate of the k-th point in the piecewise linear relation
        - b[k]: y-coordinate of the k-th point in the piecewise linear relation
    Returns the model with the piecewise linear relation on added variables x, f, and z.
    """
    K = len(a)-1
    y,z = {},{}
    for k in range(K):
        y[k] = model.addVar(lb=-GRB.INFINITY) # do not name variables for avoiding clash
        z[k] = model.addVar(vtype="B")
    #x = model.addVar(lb=a[0], ub=a[K], vtype="C")
    f = model.addVar(lb=-GRB.INFINITY)
    model.update()

    for k in range(K):
        if k>0:
            model.addConstr(y[k] >= a[k]*z[k])
        if k+1<K:
            model.addConstr(y[k] <= a[k+1]*z[k])

    model.addConstr(quicksum(z[k] for k in range(K)) == 1)
    model.addConstr(x == quicksum(y[k] for k in range(K)))

    c = [float(b[k+1]-b[k])/(a[k+1]-a[k]) for k in range(K)]
    d = [b[k]-c[k]*a[k] for k in range(K)]
    model.addConstr(f == quicksum(d[k]*z[k] + c[k]*y[k] for k in range(K)))

    return f,z

class tuplelist(list):
    """
    Tuplelist class for mypulp.py
    It works like Gurobi's tuplelist
    """
    def select(self,*args):
        """
        select elements from the tuplelist that matches the arguments
        """
        ret=[]
        for tpl in self:
            for i,element in enumerate(tpl):
                if args[i]==element or args[i]=="*":
                    pass
                else:
                    break
            else:
                ret.append(tpl)
        return ret

def multidict(dic):
    keylist =list(dic.keys())
    temp=dic[keylist[0]]
    if isinstance(temp,list):
        retList=[]
        for i in range(len(temp)):
            retList.append( {} )
        for k in keylist:
            for i in range(len(temp)):
                retList[i][k]=dic[k][i]
        retList.insert(0,keylist)
        return tuple(retList)
    else:
        retDict={}
        for k in keylist:
            retDict[k]=dic[k]
        return keylist, retDict


class Model(LpProblem):
    def __init__(self,name=""):
        LpProblem.__init__(self,name)
        self.var_id = 0
        self.constr_id =0

    class Params:
        pass
    Params.OutputFlag=0

    def addSOS(self, sos_type, var_list = []):
        if sos_type==1:
            dummy_list=[]
            for i in range(len(var_list)):
                dummy_list.append( self.addVar(vtype="B") )
            self.addConstr( quicksum( d for d in dummy_list) <=1 )
            for i in range(len(var_list)):
                self.addConstr( var_list[i] <=
                                min(var_list[i].upBound, GRB.MAXINT)*dummy_list[i] )
        elif sos_type==2:
            #assume that sum x_i <=1
            convex_comb_agg_log(self,var_list)
##            dummy_list=[]
##            for i in range(len(var_list)-1):
##                dummy_list.append( self.addVar(vtype="B") )
##            self.addConstr( quicksum( d for d in dummy_list) <=1 )
##            for i in range(len(var_list)-1):
##                self.addConstr( var_list[i]+var_list[i+1] <= dummy_list[i] )
        else:
            print("SOS Type Error")
            raise TypeError

    def setPWLObj(self, var, x, y):
        f, z = mult_selection(self, var, x, y)
        self.piece+= f

    def addVar(self,lb=0.0,ub=GRB.INFINITY,vtype="C",name=""):
        if name=="":
            self.var_id +=1
            name = "x_{0}".format(self.var_id)

        if type(lb) != type(0.0) and type(lb) != type(0):
            print("lb must be float or integer")
            raise TypeError
        if type(ub) != type(0.0) and type(lb) != type(0):
            print("ub must be float or integer")
            raise TypeError

        if vtype=="C":
            CAT=LpContinuous
            var=Variable(name=name,lowBound=lb,upBound=ub,cat=CAT)
        elif vtype=="I":
            CAT=LpInteger
            var=LpVariable(name=name,lowBound=lb,upBound=ub,cat=CAT)
        elif vtype=="B":
            CAT=LpInteger
            var=LpVariable(name=name,lowBound=0,upBound=1,cat=CAT)
        elif vtype=="S": #semi continuous
            CAT=LpContinuous
            if lb!=0:
                var=LpVariable(name=name,lowBound=0,upBound=ub,cat=CAT)
                dummy01=self.addVar(vtype="B")
                self.addConstr(var >= dummy01*lb)
                self.addConstr(var <= min(ub,GRB.MAXINT)*dummy01)
            else:
                var=LpVariable(name=name,lowBound=lb,upBound=ub,cat=CAT)
        elif vtype=="N": #semi integer
            CAT=LpInteger
            if lb!=0:
                var=LpVariable(name=name,lowBound=0,upBound=ub,cat=CAT)
                dummy01=self.addVar(vtype="B")
                self.addConstr(var >= dummy01*lb)
                self.addConstr(var <= min(ub,GRB.MAXINT)*dummy01)
            else:
                var=LpVariable(name=name,lowBound=lb,upBound=ub,cat=CAT)
        else:
            print("vtype must be 'C', 'I', 'B', 'S', or 'N'")
            raise TypeError
        var.vtype =vtype
        var.X = None
        var.RC= None
        return var

    def update(self):
        pass

    def relax(self):
        for v in self.variables():
            v.cat=LpContinuous
        return self

    def addConstr(self,Constraint=None,name="",lhs=None,sense=None,rhs=0):
        if name=="":
            self.constr_id +=1
            name = "c_{0}".format(self.constr_id)

        if sense==None:
            self +=Constraint, name #add a constraint
        else:
            if sense =="<" or sense=="<=":
                lpSense=LpConstraintLE
            elif sense==">" or sense ==">=":
                lpSense=LpConstraintGE
            else:
                sense=LpConstraintEQ
            Constraint=LpConstraint(e=lhs,sense=lpSense,rhs=rhs)
            self+= Constraint  , name
        Constraint.ConstrName=name
        Constraint.Pi = None
        Constraint.Slack =None
        return Constraint

    def setObjective(self,obj,sense,name=""):
        self +=obj,name
        self.sense=sense

    def optimize(self):

        try:
            temp=self.objective.name
        except AttributeError:
            self.setObjective(0.0, GRB.MINIMIZE)

        status = self.solve()
        if status==1:
            self.Status=GRB.Status.OPTIMAL

            self.ObjVal=value(self.objective)
            for v in self.variables():
                v.VarName=v.name
                v.X=v.varValue
                v.RC=v.dj

            for c in self.constraints:
                self.constraints[c].Pi=self.constraints[c].pi
                self.constraints[c].Slack=self.constraints[c].slack
                self.constraints[c].ConstrName=self.constraints[c].name

        elif status==-1:
            self.Status=GRB.Status.INFEASIBLE
        elif status==-2:
            self.Status=GRB.Status.UNBOUNDED
        else:
            #Not Solved = 0 or Undefined= -3
            self.Status=GRB.Status.UNDEFINED




    def getVars(self):
        return self.variables()

    def getConstrs(self):
        ret=[self.constraints[c] for c in self.constraints]
        return ret

    def write(self,filename):
        if filename[-2:]=="lp":
            self.writeLP(filename)
        elif filename[-3:]=="mps":
            self.writeMPS(filename)

class LinExpr(LpAffineExpression):
    def __init__(self,coeff=[], var=[]):
        if len(coeff)!=len(var):
            print("Lengths of coefficient and variable lists must be equal!")
            raise TypeError
        #temp=[]
        temp=zip(var,coeff)
        LpAffineExpression.__init__(self,temp)

    def addTerms(self,coeff,var):
        self.addterm(var,coeff)


class Variable(LpVariable):
    def __init__(self,name="",lowBound=0.0,upBound=GRB.INFINITY,cat=LpContinuous):
        LpVariable.__init__(self,name=name,lowBound=lowBound,upBound=upBound,cat=cat)
        self.ub   = upBound
        self.lb   = lowBound
        self.name = name

    def __repr__(self):
        return "Variable: "+ self.name +" lb="+ str(self.lb) +" ub="+ str(self.ub) + " vtype="+str(self.vtype) +" X="+str(self.X)+ " RC="+str(self.RC)



##############################################################################

if __name__ == '__main__':
#    from mypulp import *
#    m=Model()
#
#
#    x = [0,2,3,1]
#    y = [1,0,3,3]
#
#    n=len(x)
#
#    X=m.addVar(ub=3.0, name="X")
#    Y=m.addVar(ub=3.0, name ="Y")
#
#    Z=m.addVar(name ="Z")
#
#    a,b={},{}
#    for i in range(n):
#        a[i] =m.addVar(name="a({0})".format(i))
#        b[i] =m.addVar(name="b({0})".format(i))
#        m.update()
#
#    for i in range(n):
#        m.addConstr( a[i] >= x[i] -X )
#        m.addConstr( a[i] >= X-x[i] )
#        m.addConstr( b[i] >= y[i] -Y )
#        m.addConstr( b[i] >= Y-y[i] )
#
#        m.addConstr(Z>=a[i]+b[i])
#
#    m.setObjective(Z, GRB.MINIMIZE)
##    m.setObjective( quicksum( 1*a[i] for i in range(n))
##               + quicksum( 1*b[i] for i in range(n)), GRB.MINIMIZE )
#
#
#    m.optimize()
#
#    print(X.X,Y.X)
#    print(m.ObjVal)
#    for i in range(n):
#        print(a[i].X,b[i].X)
#

#    model = Model("lo1")
#
#    x = model.addVar(name='tonkoke')
#    y = model.addVar(name='kokenton')
#    z = model.addVar(name='mix')
#
#    #model.setObjective(15*x + 18*y + 30*z, GRB.MAXIMIZE)
#    model.addConstr(2*x +   y + z <= 60, name='pork')
#    model.addConstr(  x + 2*y + z <= 60, name='chicken')
#    model.addConstr(            z <= 30, name='beef')
#
#    model.optimize()
#    print( model.ObjVal )
#    for i in model.getVars():
#        print(i.VarName, i.X)

    model = Model("lo1")

    J,v = multidict({1:16, 2:19, 3:23, 4:28})

    #x1 = model.addVar(vtype="C", name="x1")
    #x2 = model.addVar(vtype="I", name="x2")
    #x3 = model.addVar(lb=0, ub=30, vtype="B", name="x3")

    x1 = model.addVar(vtype=GRB.CONTINUOUS, name="x1")
    #x1 = model.addVar(vtype="N", lb=10.5, ub=50,name="x1")
    x2 = model.addVar(vtype="C",name="x2")
    x3 = model.addVar(lb=0, ub=30, vtype="C",name="x3")

    model.update()
    model.addSOS(2,[x1,x2,x3])
    L1 = LinExpr([2,1,1],[x1,x2,x3])
    #L1=LinExpr()
    #L1.addTerms(2,x1)
    #L1.addTerms(1,x2)
    #L1.addTerms(1,x3)

    #model.addConstr(lhs=L1,sense="<=",rhs=60,name="C0")
    #model.addConstr(x1 + 2*x2 + x3 <= 60, name="C1")

    c1=model.addConstr(lhs=L1,sense="<=",rhs=60)
    model.addConstr(x1 + 2*x2 + x3 <= 60)

    model.setObjective(15*x1 + 18*x2 + 30*x3, GRB.MAXIMIZE)

    #relax=model.relax()
    #model.sos1= { 1:{x1:1,x2:2} }
    model.write("mupulp1.mps")
    model.write("mupulp1.lp")
    model.optimize()

    if model.Status == GRB.Status.OPTIMAL:
        model.write("answer.sol")
        print("Opt. Value=",model.ObjVal)
        #for v in model.getVars():
        #    print(v.VarName,v.X,v.RC)
        for v in model.getVars():
            print(v.VarName,v.X)
        for c in model.getConstrs():
            print(c.ConstrName,c.Pi)
#    m=Model()
#    x=m.addVar( name="x", vtype="I" , lb=1)
#    y=m.addVar( name="y", vtype="I" , lb=1)
#    z=m.addVar( name="z", vtype="I" , lb=1)
#    m.update()
#    m.addConstr(2*x+ y ==11)
#    m.addConstr(y+ 3*z ==14)
##m.setObjective(0,GRB.MINIMIZE)
#    m.optimize()
#    print(x.X,y.X,z.X)
