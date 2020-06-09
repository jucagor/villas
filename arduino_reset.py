from gpiozero import LED
from time import sleep

breset= LED(17)
breset.on()

while True:
    orden=int(input("ingrese 1 para prender y 0 para apagar "))
    
    print(orden)
    if orden==1:        
        breset.on()
    if orden==0:
        breset.off()
    
