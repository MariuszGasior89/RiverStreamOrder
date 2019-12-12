# !/usr/bin/env python
# -*- coding: utf-8 -*-

# skrypt do okreslania rzedowosci rzek zgodnie z metodyką Shreva w bazie MPHP

import arcpy
import time

arcpy.env.overwriteOutput = True

"""parametry programu"""
arcpy.env.workspace = r"C:\ROBOCZY\skrypty_python\ShreveStrahlerStreamOrder\MPHP.gdb"                               #geobaza robocza
rzeki = 'rzeki_san'
wezly = 'nod'

max_time = 120*60
start_time = time.time()

""" 1 - przypisanie identyfikatorow wezlow do segmentow sieci rzecznej - Warstwa rzek musi posiadac atrybuty 
[START_ID i END_ID] oznaczajace identyfikatory wezlow"""
with arcpy.da.UpdateCursor(rzeki, ['SHAPE@', 'OBJECTID', 'START_ID', 'END_ID'])as cur:
    for row in cur:
        if row[2] == 0 or row[3] == 0:
            Xs = row[0].firstPoint.X
            Xe = row[0].lastPoint.X
            Ys = row[0].firstPoint.Y
            Ye = row[0].lastPoint.Y
            END = (Xe, Ye)
            START = (Xs, Ys)

            with arcpy.da.SearchCursor(wezly, ['SHAPE@XY', 'OBJECTID'])as cur2:
                for row2 in cur2:
                    if START == row2[0]:
                        row[2] = row2[1]
                        cur.updateRow(row)
                    elif END == row2[0]:
                        row[3] = row2[1]
                        cur.updateRow(row)
            del cur2

del cur
print "koniec etapu 1"

"""2 - przypisanie wartosci rzedowosci "1" dla wszystkich zewnętrznych odcinkow rzek"""
lista = []
with arcpy.da.SearchCursor(rzeki, ['END_ID', 'ID_HYD_R_10'])as cur:
    for row in cur:
        lista.append((row[0], row[1]))
del cur


with arcpy.da.UpdateCursor(rzeki, ['OBJECTID', 'START_ID', 'KOD2', 'ID_HYD_R_10', 'PRZEBIEG'])as cur:
    for row in cur:
        war = (row[1], row[3])
        if row[2] == 0 and row[4] == 2:
            row[2] = 1
            cur.updateRow(row)

        elif row[2] == 0 and war not in lista:
            row[2] = 1
            cur.updateRow(row)
del cur
print "koniec etapu 2"

"""3 - przypisanie wartosci rzedowosci dla wewnętrznych odcinkow rzek"""
iteracja=[0]
while 0 in iteracja and (time.time() - start_time) < max_time:
    lista2 = []
    with arcpy.da.SearchCursor(rzeki, ['END_ID', 'KOD2', 'ID_HYD_R_10', 'TYP_O', 'PRZEBIEG'])as cur:
        for row in cur:
            lista2.append((row[0], row[1], row[2], row[3], row[4]))

    del cur

    with arcpy.da.UpdateCursor(rzeki, ['OBJECTID', 'START_ID', 'KOD2', 'ID_HYD_R_10', 'TYP_O'])as cur:
        for row in cur:
            if row[2] == 0:
                kody = []
                rzad = []
                i = 0
                for tupla in lista2:
                    if row[1] == tupla[0]:
                        kody.append((tupla[1], tupla[2], tupla[3], tupla[4]))
                        rzad.append(tupla[1])
                        i += 1

                        # przypisujemy rzędowość zgodnie z określonymu warunkami
                if row[4] >= 4:
                    for odc in kody:
                        if row[3] == odc[1]:
                            row[2] = odc[0]
                            cur.updateRow(row)

                elif i == 2:
                    syfony = []
                    ramie = []
                    for odc in kody:
                        syfony.append(odc[2])
                        ramie.append(odc[3])

                    if 0 not in rzad and max(syfony) >= 4:
                        for kod in kody:
                            if row[3] == kod[1]:
                                row[2] = kod[0]
                                cur.updateRow(row)

                    elif 0 not in rzad and 2 not in ramie and max(syfony) < 4:
                        row[2] = sum(rzad)
                        cur.updateRow(row)

                    elif 0 not in rzad and 2 in ramie and max(syfony) < 4:
                        row[2] = max(rzad)
                        cur.updateRow(row)

                elif i == 1 and 0 not in rzad and row[4] < 4:
                    row[2] = rzad[0]
                    cur.updateRow(row)
                elif i > 2:

                    if 0 not in rzad:
                        row[2] = sum(rzad)
                        cur.updateRow(row)

    del cur

    iteracja = []
    with arcpy.da.SearchCursor(rzeki, ['KOD2'])as cur:
        for row in cur:
            iteracja.append(row[0])
    del cur

"""4 - przypisanie wartosci rzedowosci dla ramion bocznych rzek"""
lista = []
with arcpy.da.SearchCursor(rzeki, ['KOD2'])as cur:
    for row in cur:
        lista.append(row[0])
del cur

if 0 not in lista:
    with arcpy.da.UpdateCursor(rzeki, ['OBJECTID', 'START_ID', 'KOD2', 'ID_HYD_R_10', 'PRZEBIEG'])as cur:
        for row in cur:
            if row[2] == -1:
                row[2] = 1
                cur.updateRow(row)

    del cur

print "koniec programu", round((time.time() - start_time), 0), "sek"