from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "medsys-secret-2026"

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "db.json")

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_afiliado(db, aid):
    return next((a for a in db["afiliados"] if a["id"] == aid), {})

def get_medico(db, mid):
    return next((m for m in db["medicos"] if m["id"] == mid), {})

# ─── DASHBOARD ─────────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    db = load_db()
    emps = db["empadronamientos"]
    cronicos  = [e for e in emps if e["tipo"] == "Cronico"]
    diabetes  = [e for e in emps if e["tipo"] == "Diabetes"]
    discap    = [e for e in emps if e["tipo"] == "Discapacidad"]
    pendientes  = [e for e in emps if e["estado"] == "Pendiente"]
    aprobados   = [e for e in emps if e["estado"] == "Aprobado"]
    rechazados  = [e for e in emps if e["estado"] == "Rechazado"]
    alto_costo  = db["alto_costo"]
    ac_pend     = [a for a in alto_costo if a["estado"] == "Urgente"]
    stats = {
        "total_empadronamientos": len(emps),
        "pendientes": len(pendientes),
        "aprobados": len(aprobados),
        "rechazados": len(rechazados),
        "cronicos": len(cronicos),
        "diabetes": len(diabetes),
        "discapacidad": len(discap),
        "alto_costo_total": len(alto_costo),
        "alto_costo_pendientes": len(ac_pend),
        "costo_promedio": sum(a["costo_estimado"] for a in alto_costo) // max(len(alto_costo),1),
        "proveedores": len(db["proveedores"]),
        "recetas": len(db["recetas"]),
    }
    return render_template("dashboard.html", stats=stats, emps=emps, db=db)

# ─── EMPADRONAMIENTOS ──────────────────────────────────────────────────────────
@app.route("/empadronamientos")
def empadronamientos():
    db = load_db()
    emps = db["empadronamientos"]
    tipo_f  = request.args.get("tipo", "")
    estado_f = request.args.get("estado", "")
    if tipo_f:
        emps = [e for e in emps if e["tipo"] == tipo_f]
    if estado_f:
        emps = [e for e in emps if e["estado"] == estado_f]
    enriched = []
    for e in emps:
        row = dict(e)
        row["afiliado"] = get_afiliado(db, e["afiliado_id"])
        row["medico"]   = get_medico(db, e["medico_id"])
        enriched.append(row)
    return render_template("empadronamientos.html", emps=enriched, tipo_f=tipo_f, estado_f=estado_f)

@app.route("/empadronamientos/nuevo", methods=["GET","POST"])
def nuevo_empadronamiento():
    db = load_db()
    if request.method == "POST":
        nuevo = {
            "id": f"EMP-{request.form['tipo'][:1]}-2026-{str(uuid.uuid4())[:4].upper()}",
            "tipo": request.form["tipo"],
            "afiliado_id": request.form["afiliado_id"],
            "medico_id": request.form["medico_id"],
            "fecha": datetime.now().strftime("%d/%m/%y"),
            "patologia": request.form["patologia"],
            "diagnostico": request.form["diagnostico"],
            "estado": "Pendiente",
            "tratamiento": request.form["tratamiento"]
        }
        db["empadronamientos"].append(nuevo)
        save_db(db)
        flash("Empadronamiento registrado exitosamente.", "success")
        return redirect(url_for("empadronamientos"))
    return render_template("emp_form.html", db=db)

@app.route("/empadronamientos/<emp_id>/auditar", methods=["POST"])
def auditar_empadronamiento(emp_id):
    db = load_db()
    accion = request.form.get("accion")
    for e in db["empadronamientos"]:
        if e["id"] == emp_id:
            e["estado"] = "Aprobado" if accion == "aprobar" else "Rechazado"
            break
    save_db(db)
    flash(f"Empadronamiento {accion}do correctamente.", "success")
    return redirect(url_for("empadronamientos"))

@app.route("/empadronamientos/<emp_id>")
def ver_empadronamiento(emp_id):
    db = load_db()
    emp = next((e for e in db["empadronamientos"] if e["id"] == emp_id), None)
    if not emp:
        flash("Empadronamiento no encontrado.", "error")
        return redirect(url_for("empadronamientos"))
    emp["afiliado"] = get_afiliado(db, emp["afiliado_id"])
    emp["medico"]   = get_medico(db, emp["medico_id"])
    return render_template("emp_detalle.html", emp=emp)

# ─── ALTO COSTO ────────────────────────────────────────────────────────────────
@app.route("/alto-costo")
def alto_costo():
    db = load_db()
    casos = []
    for a in db["alto_costo"]:
        row = dict(a)
        row["afiliado"] = get_afiliado(db, a["afiliado_id"])
        row["medico"]   = get_medico(db, a["medico_id"])
        casos.append(row)
    total_costo = sum(a["costo_estimado"] for a in db["alto_costo"])
    return render_template("alto_costo.html", casos=casos, total_costo=total_costo)

@app.route("/alto-costo/nuevo", methods=["GET","POST"])
def nuevo_alto_costo():
    db = load_db()
    if request.method == "POST":
        nuevo = {
            "id": f"AC-2026-{str(uuid.uuid4())[:3].upper()}",
            "afiliado_id": request.form["afiliado_id"],
            "medico_id": request.form["medico_id"],
            "fecha_prescripcion": datetime.now().strftime("%d-%m-%Y"),
            "medicamento": request.form["medicamento"],
            "tipo": request.form["tipo"],
            "prioridad": request.form["prioridad"],
            "costo_estimado": int(request.form.get("costo_estimado", 0)),
            "estado": "Urgente",
            "autorizacion": "Requerida",
            "dias": 0
        }
        db["alto_costo"].append(nuevo)
        save_db(db)
        flash("Auditoría de Alto Costo registrada.", "success")
        return redirect(url_for("alto_costo"))
    return render_template("ac_form.html", db=db)

# ─── VADEMÉCUM ─────────────────────────────────────────────────────────────────
@app.route("/vademecum")
def vademecum():
    db = load_db()
    items = db["vademecum"]
    q = request.args.get("q","").lower()
    seg = request.args.get("segmento","")
    cond = request.args.get("condicion","")
    if q:
        items = [i for i in items if q in i["monodrogra"].lower() or q in i["nombre_comercial"].lower()]
    if seg:
        items = [i for i in items if i["segmento"] == seg]
    if cond:
        items = [i for i in items if i["condicion"] == cond]
    return render_template("vademecum.html", items=items, q=q, seg=seg, cond=cond)

@app.route("/vademecum/nuevo", methods=["GET","POST"])
def nuevo_vademecum():
    db = load_db()
    if request.method == "POST":
        nuevo = {
            "id": f"V{str(len(db['vademecum'])+1).zfill(3)}",
            "monodrogra": request.form["monodrogra"],
            "nombre_comercial": request.form["nombre_comercial"],
            "presentacion": request.form["presentacion"],
            "laboratorio": request.form["laboratorio"],
            "condicion": request.form["condicion"],
            "segmento": request.form["segmento"]
        }
        db["vademecum"].append(nuevo)
        save_db(db)
        flash("Medicamento agregado al vademécum.", "success")
        return redirect(url_for("vademecum"))
    return render_template("vademecum_form.html")

@app.route("/vademecum/<item_id>/eliminar", methods=["POST"])
def eliminar_vademecum(item_id):
    db = load_db()
    db["vademecum"] = [i for i in db["vademecum"] if i["id"] != item_id]
    save_db(db)
    flash("Medicamento eliminado.", "success")
    return redirect(url_for("vademecum"))

# ─── PROVEEDORES ───────────────────────────────────────────────────────────────
@app.route("/proveedores")
def proveedores():
    db = load_db()
    return render_template("proveedores.html", proveedores=db["proveedores"])

@app.route("/proveedores/nuevo", methods=["GET","POST"])
def nuevo_proveedor():
    db = load_db()
    if request.method == "POST":
        nuevo = {
            "id": f"P{str(len(db['proveedores'])+1).zfill(3)}",
            "nombre": request.form["nombre"],
            "cuit": request.form["cuit"],
            "tipo": request.form["tipo"],
            "email": request.form["email"],
            "telefono": request.form["telefono"],
            "contactos": 1,
            "estado": "Activo"
        }
        db["proveedores"].append(nuevo)
        save_db(db)
        flash("Proveedor registrado exitosamente.", "success")
        return redirect(url_for("proveedores"))
    return render_template("proveedor_form.html")

@app.route("/proveedores/<prov_id>/eliminar", methods=["POST"])
def eliminar_proveedor(prov_id):
    db = load_db()
    db["proveedores"] = [p for p in db["proveedores"] if p["id"] != prov_id]
    save_db(db)
    flash("Proveedor eliminado.", "success")
    return redirect(url_for("proveedores"))

# ─── COMPRAS ───────────────────────────────────────────────────────────────────
@app.route("/compras")
def compras():
    db = load_db()
    ordenes = []
    for o in db["ordenes_compra"]:
        row = dict(o)
        row["proveedor"] = next((p for p in db["proveedores"] if p["id"] == o["proveedor_id"]), {})
        ordenes.append(row)
    stats = {
        "total": sum(o["total"] for o in db["ordenes_compra"]),
        "entregadas": len([o for o in db["ordenes_compra"] if o["estado"] == "Entregada"]),
        "enviadas": len([o for o in db["ordenes_compra"] if o["estado"] == "Enviada"]),
        "canceladas": len([o for o in db["ordenes_compra"] if o["estado"] == "Cancelada"]),
        "pendientes": len([o for o in db["ordenes_compra"] if o["estado"] == "Pendiente"]),
    }
    return render_template("compras.html", ordenes=ordenes, stats=stats, db=db)

@app.route("/compras/nueva", methods=["GET","POST"])
def nueva_orden():
    db = load_db()
    if request.method == "POST":
        nueva = {
            "id": f"OC-{str(len(db['ordenes_compra'])+1).zfill(3)}",
            "proveedor_id": request.form["proveedor_id"],
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "total": int(request.form.get("total", 0)),
            "estado": "Pendiente",
            "items": int(request.form.get("items", 1))
        }
        db["ordenes_compra"].append(nueva)
        save_db(db)
        flash("Orden de compra creada.", "success")
        return redirect(url_for("compras"))
    return render_template("compra_form.html", db=db)

# ─── AFILIADOS ─────────────────────────────────────────────────────────────────
@app.route("/afiliados")
def afiliados():
    db = load_db()
    q = request.args.get("q","").lower()
    afs = db["afiliados"]
    if q:
        afs = [a for a in afs if q in a["apellido"].lower() or q in a["dni"]]
    return render_template("afiliados.html", afiliados=afs)

@app.route("/afiliados/<af_id>")
def ver_afiliado(af_id):
    db = load_db()
    af = get_afiliado(db, af_id)
    emps = [e for e in db["empadronamientos"] if e["afiliado_id"] == af_id]
    for e in emps:
        e["medico"] = get_medico(db, e["medico_id"])
    recetas = [r for r in db["recetas"] if r["afiliado_id"] == af_id]
    return render_template("afiliado_detalle.html", af=af, emps=emps, recetas=recetas)

# ─── ESTADÍSTICAS ──────────────────────────────────────────────────────────────
@app.route("/estadisticas")
def estadisticas():
    db = load_db()
    emps = db["empadronamientos"]
    cronicos  = len([e for e in emps if e["tipo"] == "Cronico"])
    diabetes  = len([e for e in emps if e["tipo"] == "Diabetes"])
    discap    = len([e for e in emps if e["tipo"] == "Discapacidad"])
    pend      = len([e for e in emps if e["estado"] == "Pendiente"])
    apro      = len([e for e in emps if e["estado"] == "Aprobado"])
    rech      = len([e for e in emps if e["estado"] == "Rechazado"])
    # Auditors activity
    from collections import Counter
    medico_counts = Counter(e["medico_id"] for e in emps)
    top_auditores = []
    for mid, count in medico_counts.most_common(5):
        m = get_medico(db, mid)
        top_auditores.append({"medico": m, "count": count})
    stats = {
        "cronicos": cronicos, "diabetes": diabetes, "discapacidad": discap,
        "pendientes": pend, "aprobados": apro, "rechazados": rech,
        "total": len(emps), "top_auditores": top_auditores
    }
    return render_template("estadisticas.html", stats=stats)

# ─── RECETAS ───────────────────────────────────────────────────────────────────
@app.route("/recetas")
def recetas():
    db = load_db()
    recs = []
    for r in db["recetas"]:
        row = dict(r)
        row["afiliado"] = get_afiliado(db, r["afiliado_id"])
        row["medico"]   = get_medico(db, r["medico_id"])
        recs.append(row)
    return render_template("recetas.html", recetas=recs)

# ─── API JSON ──────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    db = load_db()
    emps = db["empadronamientos"]
    return jsonify({
        "total": len(emps),
        "pendientes": len([e for e in emps if e["estado"] == "Pendiente"]),
        "aprobados": len([e for e in emps if e["estado"] == "Aprobado"]),
        "rechazados": len([e for e in emps if e["estado"] == "Rechazado"]),
        "cronicos": len([e for e in emps if e["tipo"] == "Cronico"]),
        "diabetes": len([e for e in emps if e["tipo"] == "Diabetes"]),
        "discapacidad": len([e for e in emps if e["tipo"] == "Discapacidad"]),
        "alto_costo": len(db["alto_costo"]),
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
