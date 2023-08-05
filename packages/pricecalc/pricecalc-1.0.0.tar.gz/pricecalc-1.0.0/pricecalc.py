"""Another program in my modules called nester"""
"""
area = 470
rate = 6500
price = area * rate
print(price)
"""

""" raw_input is python2 and input() is python3"""
def areacalc():
    area = input("what is the area? \n")
    rate = input("what is the rate? \t")
    print('price','of','the','house','is',int(area)*int(rate),sep=' ',end='\n')


