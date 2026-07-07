"""Converts humanoid.urdf (font de veritat de l'estructura) a un JSON que Godot
pot llegir en runtime per construir l'Skeleton3D + meshes primitives.

No dupliquem l'URDF a mà dins Godot: aquest script el parseja i emet dades ja
en eixos de Godot. Si l'URDF canvia, es torna a executar i el JSON es regenera.

Conversio d'eixos (robot -> Godot), rotacio propia (det=+1, no reflecteix):
  robot +X (endavant) -> godot -Z (endavant)
  robot +Y (esquerra)  -> godot -X (dreta -> esquerra és +X en godot, per tant Y_r = -X_g)
  robot +Z (amunt)     -> godot +Y (amunt)

  Xg = -Yr ; Yg = Zr ; Zg = -Xr
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


def robot_to_godot(x: float, y: float, z: float) -> list[float]:
    return [-y, z, -x]


def parse_xyz(elem: ET.Element | None, attr: str = "xyz") -> tuple[float, float, float]:
    if elem is None:
        return (0.0, 0.0, 0.0)
    raw = elem.get(attr)
    if not raw:
        return (0.0, 0.0, 0.0)
    parts = [float(v) for v in raw.split()]
    return (parts[0], parts[1], parts[2])


@dataclass
class LinkData:
    name: str
    mass: float = 0.0
    geometry: dict = field(default_factory=dict)
    visual_origin_godot: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])


@dataclass
class JointData:
    name: str
    type: str
    parent: str
    child: str
    origin_godot: list[float]
    axis_godot: list[float]
    lower: float | None = None
    upper: float | None = None


def parse_geometry(visual: ET.Element | None) -> dict:
    if visual is None:
        return {"type": "box", "size": [0.1, 0.1, 0.1]}
    geom = visual.find("geometry")
    if geom is None:
        return {"type": "box", "size": [0.1, 0.1, 0.1]}
    box = geom.find("box")
    if box is not None:
        sx, sy, sz = parse_xyz(box, "size")
        # box size in robot axes (x,y,z) -> godot half-extents order matches BoxMesh.size (godot x,y,z)
        return {"type": "box", "size": [abs(sy), abs(sz), abs(sx)]}
    cyl = geom.find("cylinder")
    if cyl is not None:
        radius = float(cyl.get("radius", "0.05"))
        length = float(cyl.get("length", "0.2"))
        # cylinder axis is the link's local Z (robot) -> godot Y after conversion
        return {"type": "cylinder", "radius": radius, "height": length}
    sph = geom.find("sphere")
    if sph is not None:
        radius = float(sph.get("radius", "0.1"))
        return {"type": "sphere", "radius": radius}
    return {"type": "box", "size": [0.1, 0.1, 0.1]}


def parse_urdf(urdf_path: Path) -> dict:
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    links: dict[str, LinkData] = {}
    for link_el in root.findall("link"):
        name = link_el.get("name")
        inertial = link_el.find("inertial")
        mass_el = inertial.find("mass") if inertial is not None else None
        mass = float(mass_el.get("value")) if mass_el is not None else 0.0

        visual = link_el.find("visual")
        geometry = parse_geometry(visual)
        vis_origin = parse_xyz(visual.find("origin") if visual is not None else None)

        links[name] = LinkData(
            name=name,
            mass=mass,
            geometry=geometry,
            visual_origin_godot=robot_to_godot(*vis_origin),
        )

    joints: list[JointData] = []
    children_of: dict[str, list[str]] = {}
    for joint_el in root.findall("joint"):
        name = joint_el.get("name")
        jtype = joint_el.get("type")
        parent = joint_el.find("parent").get("link")
        child = joint_el.find("child").get("link")
        origin = parse_xyz(joint_el.find("origin"))
        axis = parse_xyz(joint_el.find("axis")) if joint_el.find("axis") is not None else (0.0, 1.0, 0.0)
        limit_el = joint_el.find("limit")
        lower = float(limit_el.get("lower")) if limit_el is not None and limit_el.get("lower") else None
        upper = float(limit_el.get("upper")) if limit_el is not None and limit_el.get("upper") else None

        joints.append(
            JointData(
                name=name,
                type=jtype,
                parent=parent,
                child=child,
                origin_godot=robot_to_godot(*origin),
                axis_godot=robot_to_godot(*axis),
                lower=lower,
                upper=upper,
            )
        )
        children_of.setdefault(parent, []).append(child)

    all_children = {j.child for j in joints}
    roots = [name for name in links if name not in all_children]
    if len(roots) != 1:
        raise ValueError(f"S'esperava una sola arrel, trobades: {roots}")
    root_link = roots[0]

    return {
        "root_link": root_link,
        "links": {name: vars(link) for name, link in links.items()},
        "joints": [vars(j) for j in joints],
    }


def load_metadata_regions(metadata_path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("regions", {})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--urdf", type=Path, default=Path(__file__).resolve().parents[3] / "manikin" / "humanoid.urdf")
    parser.add_argument("--metadata", type=Path, default=Path(__file__).resolve().parents[3] / "manikin" / "metadata.yaml")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "manikin_skeleton.json")
    args = parser.parse_args()

    scene_data = parse_urdf(args.urdf)
    scene_data["regions"] = load_metadata_regions(args.metadata)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(scene_data, f, indent=2, ensure_ascii=False)

    print(f"Escrit {args.out} amb {len(scene_data['links'])} links i {len(scene_data['joints'])} joints.")


if __name__ == "__main__":
    main()
