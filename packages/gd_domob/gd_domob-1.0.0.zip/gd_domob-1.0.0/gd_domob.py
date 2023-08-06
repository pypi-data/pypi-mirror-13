'''
step=0.1
xt=5.5
loss_changed=1.5-step*1.5*2
#print loss_changed
loss=1000
count=0
while (abs(loss_changed)>0.00000001 and  count<100):
    print 'The count is:', count
    xt=xt-step*2*xt
    #x=x-4*x**3
    #print xt
    loss_changed =abs(loss_changed-xt)
    print loss_changed,xt
    #loss = x**2
    count=count+1

print 'The opt x is:', xt
print 'The min value of func x^2+1:',xt**2+1
'''


# Code from Chapter 11 of Machine Learning: An Algorithmic Perspective
# by Stephen Marsland (http://seat.massey.ac.nz/personal/s.r.marsland/MLBook.html)

# Gradient Descent using steepest descent

from numpy import *

def Jacobian(x):
    return array([x[0], 0.4*x[1], 1.2*x[2]])

def steepest(x0):

    i = 0 
    iMax = 10
    x = x0
    Delta = 1
    alpha = 1

    while i<iMax and Delta>10**(-5):
        p = -Jacobian(x)
        xOld = x
        x = x + alpha*p
        Delta = sum((x-xOld)**2)
        print 'epoch', i, ':'
        print x, '\n'
        i += 1

x0 = array([-2,2,-2])
steepest(x0)
