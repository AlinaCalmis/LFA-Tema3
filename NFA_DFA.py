import sys
from typing import List, Tuple, Set, Dict


State = int
Word = str
Configuration = Tuple[State, Word]
Transition = Tuple[State, Word, List[State]]
EPSILON = ""

vector_of_states = []
class DFA:
    def __init__(self, numberOfStatesD, finalStatesD, statesCodificationD,
                 deltaD):
        self.numberOfStatesD = numberOfStatesD
        self.finalStatesD = finalStatesD
        self.statesCodificationD = statesCodificationD
        self.deltaD = deltaD


class NFA:
    def __init__(self, numberOfStates: int, alphabet: Set[chr], finalStates: Set[State],
                 delta: Dict[Tuple[State, chr], Set[State]]):
        self.numberOfStates = numberOfStates
        self.states = set(range(self.numberOfStates))
        self.alphabet = alphabet
        self.initialState = 0
        self.finalStates = finalStates
        self.delta = delta

    # verifica inchiderile epsilon recursiv pentru fiecare index
    def epsilon(self, currentState, eps, STATE):

        for (state, letter) in self.delta:
            if state == currentState and letter == STATE:
                eps.update(self.delta[(state, letter)])
                for i in self.delta[(state, letter)]:
                    self.epsilon( i, eps, STATE)

        return


    def epsilonClosure(self):
        eps = set()
        E = []

        # calculeaza inchiderile epsilon pentru fiecare stare in parte
        for j in self.states:
            current_state = j
            eps.add(current_state)
            for (s, l) in self.delta:
                if s == current_state and l == '':

                    # adauga toate elementele din next step-ul deltei in inchidere
                    eps.update(self.delta[(s, l)])

                    # verifica inchiderile epsilon pentru fiecare stare nou adaugata
                    for i in self.delta[(s, l)]:
                        self.epsilon(i, eps, EPSILON)

            E.append(eps)
            eps = set()

        return E

    # creeaza un DFA
    def getDFA(self, closures):
        zeroState = -1
        countStates = 0
        currentState = 0


        final = dict()
        final_DFA_states = set()

        # se porneste de la inchiderea lui 0
        vector_of_states.append(closures[0])

        # verifica daca inchiderea lui 0 este o stare finala
        for i in self.finalStates:
            for el in closures[0]:
                if i == el:
                    final_DFA_states.add(0)
                    break


        while zeroState != countStates:

            zeroState = currentState

            if zeroState < 0:
                closure = closures[0]
            else :
                cl = vector_of_states.pop(currentState)
                vector_of_states.insert(currentState,cl)
                closure = cl

            # pentru fiecare litera din alfabet, in afare de EPSILON
            # si pentru fiecare stare din inchidere se creeaza un nou vector de stari
            for letter in self.alphabet:
                new_state = set()
                if letter != EPSILON:
                    for state in closure:
                        # verifica daca este in delta si creeaza tranzitia noua
                        # catre litera curenta
                        if (state,letter) in self.delta:
                            new_state.update(self.delta[(state,letter)])

                # extrage inchiderile epsilon a fiecarui element din noua tranzitie
                aux_new_State = set()
                for element in new_state:
                    for e in closures[element]:
                        aux_new_State.add(e)

                # verifica sa nu fie goal vectorl nou creat
                if len(aux_new_State) > 0:

                    # verifica daca starea deja este inclusa
                    # daca este atunci doar include tranzitia in dictionarul final
                    # in caz contrar, adauga starea in vectorul de stari noi,
                    # adauga starea in dictionarul final  si verifica daca nu este
                    # o stare finala a noului automat
                    if aux_new_State in vector_of_states:
                        idx = vector_of_states.index(aux_new_State)
                        final[(zeroState, letter)] = idx
                    else:
                        countStates += 1
                        final[(zeroState,letter)] = countStates
                        vector_of_states.append(aux_new_State)
                        for i in self.finalStates:
                            if i in aux_new_State:
                                final_DFA_states.add(countStates)
                                break
            currentState += 1
        countStates += 1

        # adauga tranzitiile nefolosite intr-un sink state
        for state in range(countStates):
            for letter in self.alphabet:
                if (state, letter) not in final and letter != EPSILON:
                    final[(state, letter)] = countStates
        for letter in self.alphabet:
            if letter != EPSILON:
                final[(countStates, letter)] = countStates

        # toate datele se salveaza intr-un dfa
        dfa = DFA(
            numberOfStatesD = countStates,
            finalStatesD = final_DFA_states,
            statesCodificationD = vector_of_states,
            deltaD = final
        )

        return dfa

    def createDFA(self):

        # citeste nfa - ul din fisier
        alphabet = set()
        with open(sys.argv[2]) as file:
            numberOfStates = int(file.readline().rstrip())
            finalStates = set(map(int, file.readline().rstrip().split(" ")))
            delta = dict()
            while True:
                transition = file.readline().rstrip().split(" ")
                if transition == ['']:
                    break
                if transition[1] == "eps":
                    transition[1] = EPSILON

                delta[(int(transition[0]), transition[1])] = set(map(int, transition[2:]))

        for (state, w) in delta:
            alphabet.add(w)

        nfa = NFA(
            numberOfStates=numberOfStates,
            alphabet=alphabet,
            finalStates=finalStates,
            delta=delta
        )

        closures = nfa.epsilonClosure()
        dfa = nfa.getDFA(closures)

        # scrie DFA - ul in fisier
        w = open(sys.argv[3], "w")
        w.write(str(dfa.numberOfStatesD + 1))
        w.write("\n")

        for i in dfa.finalStatesD:
            w.write(str(i) + " ")

        w.write("\n")

        for (s, l) in dfa.deltaD:
            w.write(str(s) + " " +str(l) + " " + str(dfa.deltaD[(s,l)]))
            w.write("\n")