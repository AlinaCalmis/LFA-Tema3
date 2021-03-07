import sys
import NFA_DFA as DFA
ALPHABET = set()
EPSILON = ""
OR = "|"
AND = "."
OPEN = "("
CLOSED = ")"
KLEENE = "*"

# implementarea unei stive cu metodele aferente
class Stack:
    def __init__(self):
        self.stack = []

    def peek(self, idx):
        if idx < len(self.stack):
            return self.stack[-(idx + 1)]
        return None

    def push(self, element):
        self.stack.append(element)

    def pop(self):
        element = self.peek(0)
        self.stack.pop()
        return element

    def empty(self):
        return self.stack == []

    def search(self, el):
        return el in self.stack

    def size(self):
        return len(self.stack)

# instantierea tipului EPXRESIE
class Expr:
    def __str__(self):
        return ""

    def eval(self):
        return None

# instantierea expresiei de tipul OR
class Or(Expr):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __str__(self):
        return "Plus(" + self.e1.__str__() + "," + self.e2.__str__() + ")"

    def eval(self):
        return self.e1.eval() + self.e2.eval()

# instantierea expresiei de tipul AND
class And(Expr):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __str__(self):
        return "And(" + self.e1.__str__() + "," + self.e2.__str__() + ")"

    def eval(self):
        return self.e1.eval() * self.e2.eval()

# instantierea Parantezelor
class Par(Expr):
    def __init__(self, e):
        self.expr = e

    def __str__(self):
        return "Par(" + self.expr.__str__() + ")"

    def eval(self):
        return self.expr.eval()

# instantierea expresiei de tipul ALPHA (litera)
class Alpha(Expr):
    def __init__(self, alpha):
        self.alpha = alpha

    def __str__(self):
        return "Alpha(" + str(self.alpha) + ")"

    def eval(self):
        return self.alpha

# instantierea expresiei de tipul KLEENE
class Kleene(Expr):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "Kleene(" + self.expr.__str__() + ")"

# instantierea unui Parser
class Parser:
    def __init__(self):
        """
        stack -> stiva pe care se salveaza expresiile
        states -> starile automatului
        initialState -> starea initiala a utomatului
        finalStates  -> vectorul de stari finale
        transitions  -> dictionar in care sunt salvate tranzitiile
                        automatului pe fiecare dintre caracterele
                        acceptate ")(*|.[literele alfabetului]"
        """
        self.stack = Stack()
        self.states = [0, 1]
        self.initialState = 0
        self.finalStates = [1]

        self.transitions = {(0, (CLOSED, EPSILON, CLOSED)): 0}

        self.transitions[0, (KLEENE, EPSILON, KLEENE)] = 1
        for alpha in ALPHABET:
            self.transitions[0, (alpha, EPSILON, alpha)] = 1
            self.transitions[1, (alpha, EPSILON, alpha)] = 1

        self.transitions[1, (CLOSED, EPSILON, CLOSED)] = 0

        self.transitions[0, (OPEN, EPSILON, OPEN)] = 1
        self.transitions[1, (OPEN, EPSILON, OPEN)] = 1
        self.transitions[1, (OR, EPSILON, OR)] = 0
        self.transitions[1, (AND, EPSILON, AND)] = 0
        self.transitions[1, (KLEENE, EPSILON, KLEENE)] = 1

    # calculeaza urmatoarea stare si o pune pe stiva
    def nextState(self, currentState, simb):
        for (state, transition) in self.transitions:
            if state == currentState:
                if simb[-1] == transition[0]:
                    if transition[2] != EPSILON:
                        self.stack.push(transition[2])
                    return self.transitions[(state, transition)]
        return None


    def parReduction(self):
        self.stack.pop()
        expr = self.stack.pop()
        self.stack.pop()
        self.stack.push(Par(expr))

    def alphaReduction(self):
        number = self.stack.pop()
        self.stack.push(Alpha(number))

    def orReduction(self):
        expr1 = self.stack.pop()
        self.stack.pop()
        expr2 = self.stack.pop()
        self.stack.push(Or(expr2, expr1))

    def br_orReduction(self):
        br = self.stack.pop()
        expr1 = self.stack.pop()
        self.stack.pop()
        expr2 = self.stack.pop()
        self.stack.push(Or(expr2, expr1))
        self.stack.push(br)

    def andReduction(self):
        expr1 = self.stack.pop()
        # self.stack.pop()
        expr2 = self.stack.pop()
        self.stack.push(And(expr2, expr1))

    def kleeneReduction(self):
        expr = self.stack.pop()
        self.stack.pop()
        self.stack.push(Kleene(expr))

    #se reduce expresia
    #pentru inputul (4+1) -> stack :
    #                     [ ) ] ->[ CLOSED ] -> [ CLOSED 1 ] -> [ CLOSED ALPHA ] ->
    #                     -> [ CLOSED ALPHA + ] -> [ CLOSED ALPHA + 4 ] ->
    #                     -> [ CLOSED ALPHA + ALPHA ] -> [ CLOSED PLUS ] ->
    #                     -> [ CLOSED PLUS ( ] -> [ PAR ]
    def reduce(self, expr: Expr):
        # se reduce litera
        if self.stack.peek(0) in ALPHABET:
            self.alphaReduction()
            return True

        # se reduce Kleene:
        # 1. o singura data daca pe stiva sunt doua kleene star consecutive
        # 2. daca elementul imediat urmator de pe stiva este o instanta a Expresiei
        if (self.stack.peek(0) == KLEENE and self.stack.peek(1) == KLEENE) :
            self.stack.pop()
            return
        if self.stack.peek(1) == KLEENE and isinstance(self.stack.peek(0), Expr):
            self.kleeneReduction()
            return True

        # se reduce OR :
        # 1. daca expresia este nula
        # 2. daca in varful stivei se afla o paranteza inchisa, pe prima pozitie
        #    este o expresie , iar al treilea element este "|"
        # 3. daca expresia este nula , pe stiva sunt mai putin de 3 elemente
        #    si pe penultima pozitie este "|"
        if self.stack.peek(1) == OR and expr == EPSILON:
            self.orReduction()
            return True
        if self.stack.peek(2) == OR and isinstance(self.stack.peek(1), Expr) and \
                self.stack.peek(0) == OPEN :
            self.br_orReduction()
            return True
        if self.stack.peek(1) == OR and self.stack.size() < 3 and expr == EPSILON:
            self.orReduction()
            return True

        # se reduce PAR daca s-au identificat "(" si ")"
        if self.stack.peek(0) == OPEN and self.stack.peek(2) == CLOSED:
            self.parReduction()
            return True

        # se reduce AND daca sunt doua instante ale expresiei consecutive
        if isinstance(self.stack.peek(0), Expr) and isinstance(self.stack.peek(1), Expr):
            self.andReduction()
            return True

        return False

    # parcurge expresia data ca input si returneaza expresia regulata asociata
    # se opreste daca :
    # 1. nu a fost gasita o stare asociata expresiei
    # 2. pe stiva se afla mai multe instante ale expresiei
    # 3. s-a parcurs toata expresia cu succes
    def parse(self, expr):
        currentState = self.initialState

        while expr != EPSILON:
            # se analizeaza expresia din dreapta spre stanga pana expresia este nula
            currentState = self.nextState(currentState, expr)
            expr = expr[:-1]
            if currentState is None:
                break

            while self.reduce(expr):
                continue

        if expr != EPSILON and self.stack.size() != 1:
            return None

        return self.stack.pop()

# creeaza o instanta de NFA
class NFA:
    def __init__(self):
        self.nOfStates = 1
        self.initialState = 0
        self.currentState = 0
        self.finalStates = 0
        self.transitions = list(list())

        self.stack = Stack()

    def checkOperation(selfe, expr: Expr):
        if isinstance(expr, Par):
            return [OPEN, expr.expr]
        if isinstance(expr, And):
            return [AND, expr.e1, expr.e2]
        if isinstance(expr, Or):
            return [OR, expr.e1, expr.e2]
        if isinstance(expr, Kleene):
            return [KLEENE, expr.expr]

    # analizeaza expresia regulata
    def readExpr(self, expr: Expr):
        # verifica sa nu fie litera si continua citirea conform
        # tipului de expresie
        if self.checkOperation(expr) is not None:
            operation = self.checkOperation(expr)
            if operation[0] == OPEN:
                self.readExpr(operation[1])
            if operation[0] == AND:
                self.readExpr(operation[1])
                self.readExpr(operation[2])
            if operation[0] == OR:
                self.readExpr(operation[1])
                self.readExpr(operation[2])
            if operation[0] == KLEENE:
                self.readExpr(operation[1])

        # daca e litera: creste numarul de stari ,creeaza un nfa pentru litera
        #                si il pune pe stiva
        if isinstance(expr, Alpha):
            self.nOfStates += 1
            first_state = 0
            final_state = 1
            nfa = (first_state, [[first_state,expr,final_state]], final_state)
            self.stack.push(nfa)
            return

        if operation[0] == KLEENE:
            expr = self.stack.pop()
            transition = expr[1]
            initial_state = expr[0]
            self.nOfStates += 2
            final_state = expr[2] + 2

            # se incrementeaza starea initiala si finala a fiecarei tranzitii
            for t in transition:
                t[0] += 1
                t[2] += 1

            #se creeaza tranzitiile pe epsilon
            first_transition = [initial_state, EPSILON, transition[0][0]]
            reload_transition = [transition[-1][2], EPSILON, transition[0][0]]
            final_transition = [transition[-1][2], EPSILON, final_state]
            zero_transition = [initial_state, EPSILON, final_state]

            #se adauga toate tranzitiile intr-o lista de tranzitii care va fi propagata mai departe
            new_transition = list()
            new_transition.append(zero_transition)
            new_transition.append(first_transition)
            for t in transition:
                new_transition.append(t)
            new_transition.append(reload_transition)
            new_transition.append(final_transition)

            nfa = (initial_state, new_transition, final_state)
            self.stack.push(nfa)
            return
        if operation[0] == AND:
            #extrage prima expresie de pe stiva
            expr1 = self.stack.pop()

            #extrage a doua expresie de pe stiva
            expr2 = self.stack.pop()

            #extrage tranzitiile si caluleaza starile : initiala, intermediara si finala
            transition1 = expr1[1]
            transition2 = expr2[1]
            first_state = expr1[0]

            intermidiate_state = transition1[-1][2]

            transition2[0][0] = intermidiate_state
            transition2[0][2] += intermidiate_state
            for i in range(1, len(transition2)):
                transition2[i][0] += intermidiate_state
                transition2[i][2] += intermidiate_state

            final_state = transition2[-1][2]

            # creaza noua tranzitie
            transition = list()
            for t in transition1:
                transition.append(t)
            for t in transition2:
                transition.append(t)

            # creeaza un nou nfa si il trimite pe stiva
            nfa = (first_state, transition, final_state)
            self.stack.push(nfa)
            return

        if operation[0] == OR:
            #extrage expresia1 de pe stiva
            expr1 = self.stack.pop()

            #extrage expresia2 de pe stiva
            expr2 = self.stack.pop()

            initial_state = expr2[0]
            transition1 = expr1[1]
            transition2 = expr2[1]

            # se incrementeaza starea finala si initiala pentru toate
            # tranzitiile unei dintre expresii
            for t in transition2:
                t[0] += 1
                t[2] += 1

            # ultima tranzitie modificata
            final = transition2[-1][2]

            # se incrementeaza starea finala si intiala pentru toate
            # tranzitiile din cealalta expresie
            for t in transition1:
                t[0] += final + 1
                t[2] += final + 1

            # se seteaza starea finala
            final_state = transition1[-1][2] + 1

            # se creeaza ramurile
            right_transition = [initial_state, EPSILON, transition2[0][0]]
            right_end_transition = [transition2[-1][2],EPSILON, final_state]
            left_transition = [initial_state, EPSILON, transition1[0][0]]
            left_end_transition = [transition1[-1][2], EPSILON, final_state]

            # se creeaza lista de tranzitii
            transition = list()
            transition.append(right_transition)
            for t in transition2:
                transition.append(t)

            transition.append(right_end_transition)
            transition.append(left_transition)
            for t in transition1:
                transition.append(t)

            transition.append(left_end_transition)

            # se creeaza un nou nfa si se pune pe stiva
            nfa = (initial_state, transition, final_state)

            self.nOfStates += 3
            self.stack.push(nfa)
            return

    # verifica daca sunt mai multe tranzitii egale pe stari finale diferite
    def checkDoubledTransitions(self):
        transitions = self.transitions
        for i in range(0, len(transitions)):
            for j in range(i+1, len(transitions)):
                if transitions[i][0] == transitions[j][0]:
                    if transitions[i][1] == transitions[j][1]:
                        transitions[i][2].append(transitions[j][2].pop())
        for t in transitions:
            if [] in t:
                transitions.pop(transitions.index(t))

    # creeaza vectorul de tranzitii
    def computeTransitions(self):
        nfa = self.stack.pop()
        transition = nfa[1]
        self.finalStates = nfa[2]
        for t in transition:
            start = t[0]
            if isinstance(t[1], Alpha):
                alpha = t[1].alpha
            else:
                alpha = 'eps'
            end = t[2]
            self.transitions.append([start, alpha,[end]])

        self.checkDoubledTransitions()

# scrie outputul in fisier
def writeOutput(nfa: NFA):
    with open(sys.argv[2],"w") as outputFile:
        outputFile.write(str(nfa.nOfStates))
        outputFile.write("\n")
        outputFile.write(str(nfa.finalStates))
        outputFile.write("\n")
        for t in nfa.transitions:
            outputFile.write(str(t[0]))
            outputFile.write(" ")
            outputFile.write(str(t[1]))
            outputFile.write(" ")
            for next in t[2]:
                outputFile.write(str(next))
                outputFile.write(" ")
            outputFile.write("\n")
    outputFile.close()
    with open(sys.argv[3],"w") as outputFile:
        outputFile.write("1\n0\n0 b 0")

# citeste inputul din fisier
def read_input():

    with open(sys.argv[1]) as file:
        expr = file.readline()

    for i in expr:
        if i.isalpha():
            ALPHABET.add(i)


    parser = Parser()
    e = parser.parse(expr)
    nfa = NFA()
    nfa.readExpr(e)
    nfa.computeTransitions()
    writeOutput(nfa)
    DFA.NFA.createDFA(DFA.NFA)


if __name__ == '__main__':
    read_input()