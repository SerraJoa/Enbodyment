# embodiment

Substrat comú per governar cossos externs sensoritzats amb estructures neuronals
intercanviables (plug-and-play entre morfologies). La simulació genera el substrat
d'entrenament; tres branques comparteixen **un mateix maniquí** com a interfície:
visual (difusió en temps real), control (política de moviment), i tronc/interfícies
(cross-embodiment).

## El maniquí és la interfície

El mateix esquelet que el motor anima és el que la difusió rep com a conditioning i el
que la política mou. Un sol vocabulari per les tres branques. Definir-lo bé és el que
fa que parlin el mateix idioma.

## Estructura

```
embodiment/
├── README.md
├── manikin/
│   ├── humanoid.urdf      # esquelet canònic — font de veritat de l'ESTRUCTURA
│   ├── metadata.yaml      # contacte, regions (difusió), sinergies — per branca
│   └── conventions.md     # noms canònics, eixos, unitats
└── docs/
    └── architecture.md    # decisions de disseny — el PRINCIPI DE CONTROL n'és el nucli
```

## El maniquí actual

Humanoide, ~70 kg, 17 DoF actuables. Peu de **dos segments** (retropeu + avantpeu) per
push-off i *ankle strategy* sense el cost de simular dits. Articulacions amb
**compliància passiva** (stiffness/damping) — cap estabilitzador amb objectiu. Massa
dels braços suficient per a contrapès real. Identitat (cara) resolta per la branca
visual (IP-Adapter), no riggada a l'esquelet.

## El nucli: principi de control

El comportament no es programa, **emergeix** com a solució òptima. La política minimitza
el *delta* entre el flux vectorial d'intenció i el flux real, amb mínima energia. Del
detall — camps vectorials, delta com a senyal únic (extern i intern), postura
anticipatòria, DMP + control òptim, funció de recompensa — en parla
[`docs/architecture.md`](docs/architecture.md), secció 1. Llegir-la primer.

## Estat

Definició del maniquí i arquitectura. Encara sense codi de simulació ni entrenament.
Properes peces segons `docs/architecture.md` §7.
