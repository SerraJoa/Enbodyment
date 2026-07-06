# Convencions del maniquí

Aquest fitxer és la font de veritat per als **noms, eixos i unitats**. Tota branca
del projecte (física, difusió, control) llegeix aquestes convencions. Un nom no es
canvia mai un cop una branca hi depèn: s'afegeix, no es reanomena.

## Dos eixos ortogonals: estructura vs identitat

- **Estructura** = els noms de links i joints (`left_ankle`, `pelvis`...). Descriuen
  el cos. Són compartits entre totes les morfologies que comparteixin forma.
- **Identitat** = `character_id`. Descriu *qui* és aquest cos (quina cara/LoRA/embedding).
  No es barreja mai amb l'estructura. Un mateix esquelet pot portar mil identitats.

Aquesta separació és la mateixa que a nivell d'arquitectura separa el **tronc compartit**
(estructura, agnòstic del cos) de l'**encoder d'identitat** (específic). Mantenir-los
separats al maniquí és el que fa possible el plug-and-play més amunt.

## Sistema de coordenades

- Unitats: **SI** — metres, quilograms, segons, radians.
- Eixos (convenció robòtica estàndard, mà dreta):
  - **+X** = endavant (direcció de marxa frontal)
  - **+Y** = esquerra
  - **+Z** = amunt
- Arrel (root) del maniquí: **`pelvis`**. Tot penja d'aquí.
- Angles de joint: 0 = postura neutra dreta (T-pose modificada, braços avall).

## Esquema de noms

Patró: `{side}_{segment}` on `side` ∈ {`left`, `right`} o buit per als centrals.

Centrals: `pelvis`, `spine`, `chest`, `neck`, `head`.
Parells: `{side}_hip`, `{side}_knee`, `{side}_ankle`, `{side}_forefoot`,
`{side}_shoulder`, `{side}_elbow`, `{side}_wrist`.

## Peu de dos segments

Cada peu són DOS links: `{side}_foot` (retropeu, del turmell a la planta) i
`{side}_forefoot` (avantpeu), units pel joint `{side}_forefoot`. Això dona push-off
i *ankle strategy* sense el cost de simular dits. La xarxa-peu, si existeix, gestiona
aquest joint + la pressió de contacte.

## Punts de contacte

Dos tipus, etiquetats a `metadata.yaml`:
- **Locomoció**: plantes (`{side}_foot`, `{side}_forefoot`). Contacte normal.
- **Recuperació**: genolls, mans, malucs. Contacte per fall-recovery. Etiquetats des
  de l'inici encara que la política de recuperació no existeixi encara.
