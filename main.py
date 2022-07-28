import copy, os, sys
from time import time

class Nod:
    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte
        self.g = cost
        self.h = h
        self.f = self.g + self.h

    def afisDrum(self, timp, nrNoduri, nrSucc, afisLung=False, afisCost=False):
        """
        Scrie intr-un fisier de output toate drumurile gasite in urma aplicarii unui anumit algoritm (UCS, A*).

        Parameters
        ----------
        timp : str
               numarul de secunde pana la gasirea unei solutii
        nrNoduri : str
               numarul maxim de noduri aflate la un moment dat in memorie
        nrSucc : str
               numarul total de succesori
        afisLung : bool
                   Este un parametru optional cu valoarea implicita False. Daca
                   valoarea este True, scrie in fisier pe un rand nou lungimea drumului curent.
        afisCost : bool
                   Este un parametru optional cu valoarea implicita False. Daca
                   valoarea este True, scrie in fisier pe un rand nou costul total al drumului.
        """
        l = self.obtineDrum()
        f.write(
            "Solutie \n     Solutie gasita in " + timp + " secunde avand " + nrNoduri + " noduri maxime in memorie\n\n")
        f.write("     Aceasta solutie a calculat " + nrSucc + " succesori\n\n")
        for nod in l:
            if nod.parinte is not None:
                f.write("     " + str(nod) + "\n")
            else:
                f.write(str(nod) + "\n")
        if afisLung:
            f.write("     Lungime drum: " + str(len(l)) + "\n")
        if afisCost:
            f.write("     Cost: " + str(self.g) + "\n")
        f.write("\n-----------------------\n")

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l[:0] = [nod.parinte]
            nod = nod.parinte
        return l

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte

        return False

    def __str__(self):
        """
        Daca starea curenta nu este cea initiala (self.parinte is not None), se creeaza doua liste,
        prima contine toate vasele din nodul parinte care nu se afla in nodul copil, iar cea de-a
        doua toate vasele din nodul copil care nu se afla in nodul parinte. Cu ajutorul acestora, se observa
        tranzitia dintr-o stare in alta a drumului. Se apeleaza functia which care returneaza vasul din care s-a turnat,
        cati litri, culoarea apei, respectiv in ce vas s-a turnat. Dupa aceea, se afiseaza fiecare vas sub forma id,
        capacitate maxima, cantitatea de lichid din vas si culoarea apei (daca exista lichid).
        """
        sir = ""
        if self.parinte is not None:
            infoPar = self.parinte.info
            vas, vas1 = [elem for elem in infoPar if elem not in self.info], [elem for elem in self.info if
                                                                              elem not in infoPar]
            which = costTurnare(vas, vas1)
            sir = "Din vasul {} s-au turnat {} litri de apa de culoare {} in vasul {}.\n".format(which[0], which[1],
                                                                                                 which[2], which[3])
        for vase in self.info:
            try:
                sir += "     % s" % vase[0] + ": " + "% s" % vase[1][0] + " " + "% s" % vase[1][1] + " " + vase[1][
                    2] + "\n"
            except IndexError:
                sir += "     % s" % vase[0] + ": " + "% s" % vase[1][0] + " " + "% s" % vase[1][1] + "\n"
        return sir


class Graf:
    def __init__(self, fisier):
        """
        Initializeaza datele problemei. Cu ajutorul parametrului local, flag, stocam combinatiile de culori (flag are
        valoarea 0), vasele impreuna cu capacitatea, lichidul si culoarea apei (flag are valoarea 1) si lichidul,
        repectiv culoarea apei la care trebuie sa se ajunga (flag are valoarea 2).
        """
        f = open("VasInput/" + fisier)
        self.culori, self.start, self.scopuri, flag, aux = [], [], [], 0, f.readline()
        while aux:
            if aux == "stare_initiala\n" or aux == "stare_finala\n":
                nrO = 0
                flag += 1
                aux = f.readline()
                continue
            if flag == 0:
                self.culori.append(aux.split())
            elif flag == 1:
                self.start.append([nrO, [int(elem) if elem.isnumeric() else elem for elem in aux.split()]])
                nrO += 1
            else:
                self.scopuri.append([int(elem) if elem.isnumeric() else elem for elem in aux.split()])
            aux = f.readline()

    def corectitudineInput(self):
        for vase in self.start:
            if vase[1][1] > vase[1][0]:
                return 0
        return 1

    def testScop(self, nodCurent):
        """
        Pentru fiecare vas aflat in nodCurent.info, se selecteaza cantitatea de lichid si culoarea asociata.
        Acestea se adauga intr-o lista daca combinatia este in starea finala avand grija sa se puna doar unul
        dintre vasele care au aceeasi cantitate de lichid si culoare a apei, dar capacitati diferite. La final, se
        verifica daca lungimea acestei liste coincide cu lungimea starilor finale.

        Parameters
        ----------
        nodCurent : Nod

        Returns
        -------
        bool
            daca starea curenta este finala sau nu
        """
        rez, infoNod = [], nodCurent.info
        [rez.append(elem[1][1:]) for elem in infoNod if elem[1][1:] not in rez and elem[1][1:] in self.scopuri]
        return len(rez) == len(self.scopuri)

    def generareSuccesori(self, nodCurent, tipEuristica):
        """
        Se iau perechi de vase si se apeleaza functia potTurna (functie imbricata) care decide daca din vasul 1 pot turna
        in vasul 2. Daca starea noua nu se regaseste in drum, se creeaza un nod nou care se adauga in lista succesorilor
        cu costul determinat pana aici + 1.

        Parameters
        ----------

        nodCurent : Nod
        tipEuristica : str
                decide metoda de calcul a estimarii din starea curenta pana in starea finala
        Returns
        -------

        succesori : list
                toate mutarile posibile pentru starea curenta
        """

        def potTurna(vas1, vas2):
            """
            Se creeaza o copie deep a celor doua vase. Daca vasul 1 nu are lichid sau daca vasul 2 este umplut la
            capacitate maxima, functia returneaza vasele nemodificate.
            Altfel, se toarna apa din vasul 1 in vasul 2 cat timp mai exista lichid si vasul 2 nu a atins capacitatea
            maxima. Daca vasul 2 nu are culoarea nedefinita (combinatie de culori nestiute), se verifica daca culoarea
            vasului 1 impreuna cu cea a vasului 2 formeaza o culoare cunoscuta. Daca da, culoarea vasului 2 o preia
            (vasul 2 este mereu cel in care se toarna). Daca nu, se verifica ca vasele sa aiba culori diferite inainte
            de a se pune identificatorul nedefinit in vasul 2. La final, se verifica daca mai exista lichid in vasul 1.
            Daca nu mai exista, se scoate culoarea acestuia. Se returneaza vasele modificate.

            Parameters
            ----------
            vas1 : list
            vas2 : list
            """
            copieV1, copieV2 = copy.deepcopy(vas1), copy.deepcopy(vas2)
            lichid1, cap2, lichid2 = vas1[1][1], vas2[1][0], vas2[1][1]
            capRamas = cap2 - lichid2
            if lichid1 == 0 or capRamas == 0:
                return vas1, vas2
            while lichid1 > 0 and capRamas > 0:
                lichid1, lichid2, capRamas = lichid1 - 1, lichid2 + 1, capRamas - 1

            copieV1[1][1], copieV2[1][1] = lichid1, lichid2
            if len(copieV2[1]) == 3:
                if copieV2[1][2] != "nedefinit":
                    for elem in self.culori:
                        if (elem[0] == copieV1[1][2] and elem[1] == copieV2[1][2]) or (
                                elem[1] == copieV1[1][2] and elem[0] == copieV2[1][2]):
                            copieV2[1][2] = elem[2]
                            break
                    else:
                        if copieV1[1][2] != copieV2[1][2]:  # daca nu au acceasi culoare
                            copieV2[1][2] = "nedefinit"
            else:
                copieV2[1].append(copieV1[1][2])
            if lichid1 == 0:
                copieV1[1].pop()

            return copieV1, copieV2

        succesori, vase = [], nodCurent.info
        nrVase = len(vase)
        for i in range(nrVase):
            for j in range(nrVase):
                if i != j:
                    copieVas = copy.deepcopy(vase)
                    nouVas1, nouVas2 = potTurna(vase[i], vase[j])
                    copieVas[i], copieVas[j] = nouVas1, nouVas2
                    if not nodCurent.contineInDrum(copieVas):
                        nodNou = Nod(copieVas, nodCurent, nodCurent.g + 1, self.calculeazaEuristica(copieVas,
                                                                                                    tipEuristica))
                        succesori.append(nodNou)
        return succesori

    def calculeazaEuristica(self, infoNod, tipEuristica):
        """
        In functie de valoarea parametrului tipEuristica, se decide ce euristica se apeleaza pentru nodul curent.
        Daca tipEuristica este un string vid, atunci se returneaza 0, fapt ce ne spune ca nu avem nevoie de nicio euristica
        Daca tipEuristica este un string nevid, atunci se apeleaza functia corespunzatoare stringului dat.

        Parameters
        ----------

        infoNod : Nod
        tipEuristica : str
        """
        if tipEuristica == "":
            return 0
        if tipEuristica == "euristicaBanala":
            return self.euristicaBanala(infoNod)
        if tipEuristica == "euristicaAdmisibila":
            return self.euristicaAdmisibila(infoNod)
        if tipEuristica == "euristicaAdmisibila1":
            return self.euristicaAdmisibila1(infoNod)
        if tipEuristica == "euristicaNeadmisibila":
            return self.euristicaNeadmisibila(infoNod)

    def euristicaBanala(self, infoNod):
        """
        Pentru fiecare vas, se alege cantitatea de lichid impreuna cu culoarea apei si se adauga intr-o lista daca aceasta
        combinatie este in starea finala. Se pastreaza doar unul dintre vasele care au aceeasi cantitate de lichid si
        aceeasi culoare a apei, dar capacitati diferite.

        Parameters
        ----------
        infoNod : list

        Returns
        -------
        bool
            0 daca starea curenta este in starea finala, altfel 1
        """
        rez = []
        [rez.append(elem[1][1:]) for elem in infoNod if elem[1][1:] not in rez and elem[1][1:] in self.scopuri]
        return 0 if len(rez) == len(self.scopuri) else 1

    def euristicaNeadmisibila(self, infoNod):
        """
        Pentru fiecare culoare din starea finala se cauta combinatia asociata in lista de culori. Fiecare combinatie,
        apeleaza functia obtineCombinatii unde se trimit lista formata din combinatia gasita si cantitatea de lichid
        din starea finala, impreuna cu vasele fara id.

        Parameters
        -----------
        infoNod: list

        Returns
        -------
        cost : int
            costul estimativ din starea curenta pana in starea finala
        """
        cost = 0
        for stare in self.scopuri:
            for elem in self.culori:
                if stare[1] == elem[2]:
                    cost += obtineCombinatii(elem + [stare[0]], [elem[1] for elem in infoNod])
        return cost

    def euristicaAdmisibila(self, infoNod):
        """
        Pentru fiecare vas, se alege cantitatea de lichid impreuna cu culoarea apei si pentru fiecare combinatie care
        nu se afla in starea finala se adauga 1 la estimare. Altfel spus, se verifica cate vase din starea curenta nu
        se afla in starea finala

        Parameters
        ----------
        infoNod : list

        Returns
        -------
        estimare : int
            costul estimativ din starea curenta pana in starea finala
        """
        estimare = 0
        for vas in infoNod:
            if vas[1][1:] not in self.scopuri:
                estimare += 1
        return estimare

    def euristicaAdmisibila1(self, infoNod):
        """
        Se parcurg vasele din starea finala, calculandu-se valoarea absoluta dintre cantitatea de apa finala si
        cantitatea de lichid din fiecare vas al starii curente.

        Parameters
        ----------
        infoNod : list

        Returns
        -------
        estimare : int
            costul estimativ din starea curenta pana in starea finala
        """
        estimare = 0
        for stFinal in self.scopuri:
            for vas in infoNod:
                estimare += abs(stFinal[0] - vas[1][1])
        return estimare


def costTurnare(vas, vas1):
    """
    Vas si vas1 contin lista vaselor parinte, respectiv lista vaselor copil, modificate. Se efectueaza diferenta dintre 
    cantitatea de lichid din primul vas din lista vas si vasul corespondent(cu acelasi id) din lista vas1. Diferenta decide 
    care este vasul din care s-a turnat apa si se returneaza id-ul, cantitatea de lichid turnat, culoarea apei din vasul in 
    care s-a turnat si id-ul vasului in care s-a turnat. 

    Parameters:
    ----------
    vas : list
    vas1 : list

    Returns
    -------
    vas
    """
    if vas[0][1][1] - vas1[0][1][1] > 0:
        return vas[0][0], vas[0][1][1] - vas1[0][1][1], vas[0][1][2], vas[1][0]
    return vas[1][0], vas1[0][1][1] - vas[0][1][1], vas[1][1][2], vas[0][0]


def costTurnare1(vas1, vas2, capFinala):
    """
    Daca vas2 are culoare (len(vas2) == 3), se verifica daca se poate turna apa din primul vas in acesta astfel incat sa
    nu depaseasca cantitatea de lichid din starea finala. Daca vas2 nu are culoare, se verifica daca se poate turna apa
    din vas 1 astfel incat acesta sa ramana cu cantitatea de lichid din starea finala.

    Parameters
    ----------
    vas1 : list
    vas2 : list
    capFinala : int

    Returns
    -------
    cost : int
        cantitatea de lichid turnat
    """
    lichid1, cap2, lichid2, cost = vas1[1], vas2[0], vas2[1], 0
    capRamas = cap2 - lichid2
    if len(vas2) == 3:
        while lichid1 > 0 and capRamas > 0 and lichid2 < capFinala:
            lichid1, lichid2, capRamas, cost = lichid1 - 1, lichid2 + 1, capRamas - 1, cost + 1
    else:
        while lichid1 > 0 and capRamas > 0 and lichid1 > capFinala:
            lichid1, lichid2, capRamas = lichid1 - 1, lichid2 + 1, capRamas - 1
        return lichid2 if lichid1 == capFinala else 0

    return cost


def obtineCombinatii(cul, vase):
    """
    Se parcurge fiecare vas, alegandu-se vasele care contin culori pentru care se stie rezultatul combinarii. Vasele libere
    se ignora. Pentru fiecare, se verifica daca se poate turna apa din primul vas in al doilea, iar rezultatul este adaugat
    intr-o lista. Dupa aceea, se verifica vasele care au deja culoarea rezultat. Pentru acestea, se verifica daca se poate
    turna apa din ele intr-un vas liber astfel incat primul vas sa ramana cu cantitatea de lichid din starea finala.
    Rezultatul se adauga in vectorul de costuri.

    Parameters
    ----------
    cul : list
    vase : list

    Returns
    -------
    int
        minimul dintre costuri (>0) daca lista este nevida, altfel se ia costul din starea finala daca nu putem aproxima
        un cost
    """
    costuri = []
    for vas in vase:
        for vass in vase:
            try:
                if vas[2] in cul[0:2] and vass[2] in cul[0:2] and vas[2] != vass[2]:
                    costuri.append(costTurnare1(vas, vass, cul[3]))
            except IndexError:
                pass

    for vas in vase:
        try:
            if vas[2] == cul[2]:
                for vass in vase:
                    if len(vass) == 2:
                        costuri.append(costTurnare1(vas, vass, cul[3]))
        except IndexError:
            pass

    lst = [elem for elem in costuri if elem > 0]
    return cul[3] if len(lst) == 0 else min(lst)


def UCS(gr, nrSol=1, timeout=0, tipEuristica=""):
    Open, timp, nrSucc, maxi = [Nod(gr.start, None)], time(), 0, 1
    flag = False if timeout == 0 else True

    while len(Open) > 0:
        nodCurent = Open.pop(0)

        if flag:
            if round(time() - timp) == timeout:
                f.write("Solutia a iesit din timp\n")
                break

        if gr.testScop(nodCurent):
            nodCurent.afisDrum(str(time() - timp), str(maxi), str(nrSucc), True, True)
            nrSol -= 1
            if nrSol == 0:
                return

        succesori = gr.generareSuccesori(nodCurent, tipEuristica)
        nrSucc += len(succesori)
        for s in succesori:
            Open.append(s)
        maxi = max(maxi, len(Open) + len(succesori))
        Open = sorted(Open, key=lambda x: x.g)


def aStarOptim(gr, timeout=0, tipEuristica=""):
    Open, closed, timp, nrSucc, maxi = [Nod(gr.start, None)], [], time(), 0, 1
    flag = False if timeout == 0 else True

    while len(Open) > 0:
        nodCurent = Open.pop(0)
        closed.append(nodCurent)

        if flag:
            if round(time() - timp) == timeout:
                f.write("Solutia a iesit din timp\n")
                f.close()
                return

        if gr.testScop(nodCurent):
            nodCurent.afisDrum(str(round((time() - timp))), str(maxi), str(nrSucc), afisLung=True, afisCost=True)
            return

        lSuccesori = gr.generareSuccesori(nodCurent, tipEuristica)
        lSuccesoriCopy = lSuccesori.copy()
        maxi = max(maxi, len(Open) + len(closed) + len(lSuccesori))
        nrSucc += len(lSuccesori)
        for s in lSuccesoriCopy:
            gasitOpen = False
            for elem in Open:
                if s.info == elem.info:
                    gasitOpen = True
                    if s.f < elem.f:
                        Open.remove(elem)
                    else:
                        lSuccesori.remove(s)
                    break
            if not gasitOpen:
                for elem in closed:
                    if s.info == elem.info:
                        if s.f < elem.f:
                            closed.remove(elem)
                        else:
                            lSuccesori.remove(s)
                        break
        for s in lSuccesori:
            Open.append(s)
        Open = sorted(Open, key=lambda x: x.f)


def aStar(gr, nrSol=1, timeout=0, tipEuristica=""):
    Open, timp, nrSucc, maxi = [Nod(gr.start, None)], time(), 0, 1
    flag = False if timeout == 0 else True

    while len(Open) > 0:
        nodCurent = Open.pop(0)

        if flag:
            if round(time() - timp) == timeout:
                f.write("Solutia a iesit din timp\n")
                break

        if gr.testScop(nodCurent):
            nodCurent.afisDrum(str(round((time() - timp))), str(maxi), str(nrSucc), afisLung=True, afisCost=True)
            nrSol -= 1
            if nrSol == 0:
                return

        succesori = gr.generareSuccesori(nodCurent, tipEuristica)
        nrSucc += len(succesori)
        for s in succesori:
            Open.append(s)
        maxi = max(maxi, len(Open) + len(succesori))
        Open = sorted(Open, key=lambda x: x.f)


def idaStar(gr, nrSol=1, timeout=0, tipEuristica=""):
    def construiesteDrum(nodCurent):
        nonlocal maxi, nrSucc, nrSol

        nrSucc -= 1
        if nodCurent.f > limita:
            return nrSol, nodCurent.f

        if flag:
            if round(time() - timp) == timeout:
                f.write("Solutia a iesit din timp\n")
                return nrSol, "gata"

        if gr.testScop(nodCurent) and nodCurent.f == limita:
            nodCurent.afisDrum(str(round((time() - timp))), str(maxi), str(nrSucc), afisLung=True, afisCost=True)
            nrSol -= 1
            if nrSol == 0:
                return nrSol, "gata"

        maxi += 1
        succesori, minim = gr.generareSuccesori(nodCurent, tipEuristica), float("inf")
        nrSucc += len(succesori)
        for s in succesori:
            nrSol, rez = construiesteDrum(s)
            if rez == "gata":
                return nrSol, "gata"
            minim = min(minim, rez)
        return nrSol, minim

    limita, nodStart = gr.calculeazaEuristica(gr.start, tipEuristica), Nod(gr.start, None, 0)
    maxi, nrSucc, timp = 0, 0, time()
    flag = False if timeout == 0 else True

    while True:
        nrSol, rez = construiesteDrum(nodStart)
        if rez == "gata":
            break
        if rez == float("inf"):
            f.write("Nu exista solutii\n")
            break
        limita = rez


if __name__ == "__main__":
    print("1 ------> A* optim\n2 ------> A*\n3 ------> UCS\n4 ------> IDA*\n")
    for numeFisier in os.listdir(sys.argv[1]):
        print("Input:", numeFisier)
        op = int(input("Optiunea dumneavostra:"))
        gr = Graf(numeFisier)
        if not gr.corectitudineInput():
            break
        with open("VasInput/" + numeFisier) as file:
            f = open(sys.argv[2] + '/' + "output_" + numeFisier, "w")
            if op == 1:
                #aStarOptim(gr, int(sys.argv[4]), "euristicaBanala")
                aStarOptim(gr, int(sys.argv[4]), "euristicaNeadmisibila")
                # aStarOptim(gr, int(sys.argv[4]), "euristicaAdmisibila")
                # aStarOptim(gr, int(sys.argv[4]), "euristicaAdmisibila1")
            elif op == 2:
                # aStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaBanala")
                # aStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaNeadmisibila")
                # aStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaAdmisibila")
                aStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaAdmisibila1")
            elif op == 3:
                UCS(gr, int(sys.argv[3]), int(sys.argv[4]))
            elif op == 4:
                 #idaStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaBanala")
                 #idaStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaNeadmisibila")
                 idaStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaAdmisibila")
                 #idaStar(gr, int(sys.argv[3]), int(sys.argv[4]), "euristicaAdmisibila1")
            else:
                print("Optiune gresita")
                break