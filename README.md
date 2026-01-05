---
title: "Spletne tehnologije – Vaja 3: PageRank"
author: "Igor Polajžer"
date: "5. januar 2026"
---

# Spletne tehnologije – Vaja 3: PageRank

Pri tej vaji sem implementiral algoritem **PageRank** za ocenjevanje pomembnosti spletnih strani na podlagi strukture povezav med njimi. Splet je bil modeliran kot usmerjen graf, nad katerim je bil izveden iterativni izračun PageRank vrednosti z uporabo faktorja teleportacije.

V nadaljevanju sta prikazana grafa izvajanja algoritma nad spletnima stranema **https://google.com** in **https://feri.um.si**. Za obe strani je bil algoritem pognan z globino preiskovanja 3. Izhodiščno vozlišče je označeno z zeleno barvo, pet vozlišč z najvišjim PageRankom pa je poudarjenih z različnimi barvami in velikostmi. Ob vsakem vozlišču je prikazana izračunana PageRank vrednost.

![feri.um.si_crawler_graph.gv-1.png](images%2Fferi.um.si_crawler_graph.gv-1.png)

![google.com_crawler_graph.gv-1.png](images%2Fgoogle.com_crawler_graph.gv-1.png)