__author__ = 'Administrator'

face=[85]
unface=[(23,[True,1])]
i=0
PrimaryKey=[{"pos":i,"id":u[0],"support":face[0]} for u in unface if isinstance(u[1],bool)==True]
print(PrimaryKey)


