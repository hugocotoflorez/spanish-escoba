import random

class card:
    
    def __init__(self,number,name,palo) -> None:
        self.number = number
        self.name = name
        self.palo = palo
        
        
def get_baraja():
    cards = []
    for palo in ('oros','espadas','copas','bastos'):
        for value in range(1,11):
            match value:
                case 1:
                    name = 'as'
                case 8:
                    name = 'sota'
                case 9:
                    name = 'caballo'
                case 10:
                    name = 'rey'
                case _: 
                    name = str(value)
                
            name = f'{name} de {palo}'
            cards.append(card(value,name,palo))
            
    return cards


def barajar(baraja)->None:
    random.shuffle(baraja)    

            
            
    
        
    