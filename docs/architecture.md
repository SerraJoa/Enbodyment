# Arquitectura

Aquest document fixa les decisions de disseny del projecte. L'ordre no és casual:
el **principi de control** és el nucli del qual pengen les altres branques, i està
escrit abans de tocar cap entrenament perquè tot s'hi mesura contra.

---

## 0. Visió

Un substrat comú que permeti que una estructura neuronal governi cossos externs
sensoritzats, amb blocs intercanviables (plug-and-play entre morfologies). La
simulació genera el substrat d'entrenament. Tres branques comparteixen **un mateix
maniquí** com a interfície:

- **Visual** — difusió condicionada en temps real (posa la "pell" i l'estil).
- **Control** — la política que mou el cos.
- **Interfícies/tronc** — el que fa possible el cross-embodiment.

El maniquí és la interfície compartida: el mateix esquelet que el motor anima, que
la difusió rep com a conditioning, i que la política mou. Un sol vocabulari.

---

## 1. Principi de control (NUCLI)

> El comportament correcte no es programa com a regles ni s'afegeix com a mòduls.
> És l'**única solució òptima** d'un problema ben plantejat, i el cos hi arriba
> perquè no hi ha res més barat.

### 1.1 Estat com a camps vectorials, no punts

L'estat rellevant no són posicions instantànies sinó **camps vectorials** — direcció
i força, contínues en el temps:

- **Flux d'intenció**: cap on vol anar el cos, amb quina força. Per moviments cíclics
  (caminar) té forma sinusoidal/rítmica.
- **Flux real**: cap on va de fet el cos ara.

### 1.2 El senyal és el DELTA

Cada part del cos no s'alinea amb la intenció ni amb l'estat real, sinó amb la
**diferència entre els dos** — el delta vectorial. Aquesta diferència pot originar-se:

- **de fora**: una força externa (empenta) desvia el flux real de l'intenció;
- **de dins**: el propi cicle del moviment demana que el cos ja estigui col·locat
  per a la fase següent.

Ambdós casos són **el mateix acte**: reduir el delta entre flux real i flux desitjat.
No hi ha un "control d'equilibri" i un "control de moviment" separats. Hi ha una sola
dinàmica que persegueix alinear real amb intenció, contínuament.

Corol·lari (postura anticipatòria): si les cames caminen però el tronc queda penjant,
hi ha un delta entre la configuració actual i la que *facilitaria el proper pas*. El
cos es col·loca no per "estar dret" sinó per **minimitzar l'energia del proper pas**.
La postura és predictiva, no reactiva.

### 1.3 Mínima energia com a selector

Entre totes les formes de reduir el delta, el sistema tria la de **menor cost
energètic integrat en el temps** (no instant a instant). Minimitzar energia sobre un
horitzó *obliga* a anticipar: per això la postura anticipatòria emergeix sola, sense
cap regla que la imposi.

### 1.4 Marc formal

Això no és analogia; és el marc matemàtic:

- Un camp d'intenció amb **atractor** al qual el sistema reflueix després de
  pertorbacions = **Dynamic Movement Primitives** (Ijspeert/Schaal). El terme
  sinusoidal del caminar és el component oscil·latori d'un DMP rítmic.
- El criteri de mínima energia = **control òptim**. Contrapès, equilibri i postura
  anticipatòria són *conseqüències* de la funció objectiu, no mòduls afegits.

### 1.5 Funció de recompensa del projecte

La política minimitza, integrat en el temps:

```
cost = w_align · |delta(flux_real, flux_intencio)|  +  w_energy · energia_gastada
```

Res més. **Tot** el comportament desitjat (equilibri, contrapès, col·locació del
tronc, compensació d'empentes, push-off) emergeix d'aquests dos termes. Si un
comportament no emergeix, es revisa el plantejament del delta o dels pesos — no
s'afegeix una regla ad hoc.

---

## 2. Substrat passiu (el cos)

El cos **no** porta cap estabilitzador amb objectiu de postura. Un estabilitzador
que corregeix cap a la vertical competiria amb la intenció del moviment (frenaria una
inclinació volguda per arrencar a córrer). En comptes d'això:

- Cada joint té només propietats **passives**: `stiffness`/`damping` (moll +
  esmorteïdor virtuals). Definides a `<dynamics>` de l'URDF.
- El cos ofereix **elasticitat i inèrcia**, no correcció. És un recurs mecànic
  disponible, no un agent amb voluntat.
- La massa dels braços és **deliberadament suficient** per a contrapès real.

El contrapès, doncs, no és un mòdul: és el que resulta de minimitzar el delta amb
mínima energia quan una força desvia el cos. Ja hi és, si la recompensa és la de §1.5.

---

## 3. Jerarquia i subsidiarietat

Principi: cada nivell actua fins al límit de la seva **tolerància** i només escala
l'excés (discriminació de tasques). Model biològic: *ankle strategy* — el turmell
absorbeix pertorbacions petites localment i ràpid; quan superen el seu sobre, escala
al maluc/cama.

| Nivell | Freqüència | Implementació | Ambició |
|--------|-----------|---------------|---------|
| Llaç baix (òrgan) | ~1 kHz | Programació pura + xarxa petita | Especialització màxima, cap generalització |
| Llaç alt (organització) | ~20-50 Hz | Tronc compartit/generalista | Intencions abstractes, agnòstic del cos |

**Interfície entre nivells**: el nivell alt NO emet torques (seria fràgil i específic
del cos), sinó **objectius/intencions** que cada òrgan tradueix finament. Patró:
"el planificador proposa, el controlador local disposa" (HRL amb options/goals).

**Què veu el nivell alt**: no cada actuador, sinó **estat centroidal + configuració de
contacte**. En termes de balanç, el punt d'abstracció correcte no és el CoM sinó el
**ZMP/centre de pressió** (el punt on la reducció de forces esdevé força pura sense
moment residual). El nivell alt ha de veure el polígon de suport perquè el ZMP hi
quedi dins.

### 3.1 Quan un òrgan mereix ser xarxa (no simple ajust)

Un òrgan justifica ser xarxa si compleix ≥1 de:
1. Té **més DoF** dels que el nivell alt vol gestionar (ex: dits — descarrega el gran).
2. Opera a **freqüència més alta** (tanca un llaç que el gran no pot per latència).
3. Explota **informació local** privilegiada (pressió planta a planta, micro-lliscament).

Si no en compleix cap → és ajust fi → programació pura o plegat dins del gran.

### 3.2 Sinergies i gating per consonància

Capa **facilitadora** (no correctiva) que amplifica moviment alineat amb la intenció:

- **Sinergies motores**: grups de joints que s'activen coordinadament (en bloc),
  no independentment. Declarades a `metadata.yaml` → `synergies`.
- **Gating per consonància**: una sinergia s'encén segons com d'**alineada** està amb
  la intenció (producte escalar direcció-sinergia · direcció-intenció). Alineació
  alta → gate obert. Baixa o oposada → baix perfil.
- Distinció clau: un reflex clàssic s'activa per **desviació** (error → corregeixo) i
  pot lluitar contra la intenció. Aquest gating s'activa per **consonància** (va a
  favor → amplifico) i per construcció mai lluita contra la intenció.

Ruta: base explícita de sinergies (bootstrap) → refinament per reforç amb recompensa
de fluïdesa (via §1.5). Mateixa forma que tot el projecte: base sòbria + capa apresa.

---

## 4. Estratègia d'entrenament

- **Imitació + reforç**, no currículum morfològic. Uns clips de mocap/animació donen
  inicialització que ja "sap" la forma del moviment; el reforç refina i fa robust.
  Evita que l'RL des de zero malgasti milions de passos.
- **Currículum segur**: gradua dificultat en **pertorbacions i terreny** (pla →
  irregular → empentes), NO en morfologia. Mateix cos, món cada cop més dur.
- **Residual sobre substrat, no sobre estabilitzador**: la política aprèn sobre el cos
  passiu (§2), no sobre un controlador d'equilibri. No hi ha base amb objectiu de què
  aprendre manies.
- **Sobre-provisionar els nivells baixos**: entrenar òrgans/sinergies amb una
  distribució de comandes deliberadament més ampla que la que el nivell alt demanarà,
  perquè siguin robustos a qualsevol cosa (evita *distribution shift* entre nivells).
- **Fall-recovery** com a política separada, activada quan l'estat surt del sobre segur
  (CoM fora del polígon). Els punts de contacte de recuperació ja estan etiquetats a
  `metadata.yaml`.

---

## 5. Branca visual (resum)

Pipeline de difusió en temps real que posa estil i identitat sobre el maniquí:
ControlNet (depth/pose des dels render passes del motor) + IP-Adapter FaceID per
identitat (no LoRA per cara, que no escala en runtime) + LCM/destil·lació de passos +
StreamDiffusion amb *latent recycling* (init des del frame anterior, denoise baix) +
warp per **motion vectors ground-truth** del motor (repintar només el que canvia) +
interpolació piramidal (keyframe + RIFE + blur segons magnitud de moviment).

Els render passes que la difusió necessita (depth, normals, motion vectors, z-buffer
per desoclusions, màscares per regió) són **G-buffer que el motor ja genera nativament**.

### Hardware
- **Strix Halo (128 GB unificats)**: memòria abundant (tot resident sense swap), però
  ample de banda ~256 GB/s (vs ~1000 d'una 4090) i sense TensorRT (ROCm/ONNX). Objectiu
  realista: **temps real tou**, 10-15 fps a 512px als keyframes + interpolació fins a
  24-30. Node d'inferència i pipeline visual, NO entrenament RL massiu.
- **Entrenament RL massiu**: territori CUDA/clúster (Isaac Lab/MJX). Fora de l'Strix Halo.

---

## 6. Simulació

- **Branca control/RL**: Isaac Lab/Sim, MuJoCo/MJX o Genesis — física rígida precisa,
  massivament paral·lela. Clau: *domain randomization* (masses, friccions, latències)
  per sim-to-real.
- **Branca visual**: motor de joc (Unreal/Godot) com a font de G-buffer. Maniquís
  flat-shaded → render barat → capejar a 512 i deixar el múscul per la part neuronal.

---

## 7. Fases (cada peça és un projecte)

1. Pipeline visual (autònom, dona valor sol).
2. Política per **una** morfologia (aquest maniquí) amb sim-to-real bàsic.
3. Segona morfologia → aquí es descobreix què és interfície i què és tronc.
4. Espai interoceptiu compartit (estat intern agregat: càrrega, esforç, marge).

L'estat interoceptiu no és decoratiu: és el que el coordinador necessita per no demanar
impossibles (§3, "veure el marge de cada òrgan"), i el que la branca visual pot
renderitzar com a "tauler de sensacions".
