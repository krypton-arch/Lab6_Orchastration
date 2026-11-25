import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="{top}" w:type="dxa"/>
        <w:bottom w:w="{bottom}" w:type="dxa"/>
        <w:left w:w="{left}" w:type="dxa"/>
        <w:right w:w="{right}" w:type="dxa"/>
    </w:tcMar>''')
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''<w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
        <w:insideV w:val="none"/>
    </w:tblBorders>''')
    tblPr.append(borders)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        <w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
    </w:tcBorders>''')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(9.0)
    run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_callout(doc, text, title="NOTE"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EFF6FF")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="none"/>
        <w:left w:val="single" w:sz="28" w:space="0" w:color="2563EB"/>
        <w:bottom w:val="none"/>
        <w:right w:val="none"/>
    </w:tcBorders>''')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"[{title}] ")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(10)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
    
    run_b = p.add_run(text)
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_figure(doc, img_path, caption):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = "Calibri"
        run_cap.font.size = Pt(9.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

def build_docx():
    doc = docx.Document()
    
    # Page Setup
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
        # Header / Footer
        header = section.header
        p_head = header.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_head = p_head.add_run("DevOps Laboratory \u2022 Lab 6: Jobs, CronJobs, ConfigMaps, Secrets & Helm")
        r_head.font.name = "Calibri"
        r_head.font.size = Pt(8.5)
        r_head.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_foot = p_foot.add_run("Department of Computer Science & Engineering \u2022 CHRIST (Deemed to be University)")
        r_foot.font.name = "Calibri"
        r_foot.font.size = Pt(8.5)
        r_foot.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Calibri'
    normal_font.size = Pt(11)
    normal_font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # Document Header / Banner
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(2)
    r_uni = p_meta.add_run("CHRIST (DEEMED TO BE UNIVERSITY), BANGALORE\nDEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
    r_uni.font.name = "Calibri"
    r_uni.font.size = Pt(10)
    r_uni.font.bold = True
    r_uni.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("DevOps Engineering Laboratory Report \u2022 Lab 6\nKubernetes Batch Processing, Decoupled Configuration & Helm Application Packaging")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(19)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Declarative Jobs, Scheduled CronJobs, Secret Masking, ConfigMap Volume Mounts, and Automated Helm 3 Lifecycle Operations")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    # Academic Meta Table
    tbl_meta = doc.add_table(rows=5, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course Name & Code", "DevOps Engineering Laboratory (5th Trimester, MCA / B.Tech)"),
        ("Laboratory Topic", "Kubernetes Jobs, CronJobs, ConfigMaps, Secrets, and Helm Deployment"),
        ("Target Cluster & Tools", "Kubernetes v1.36.1 (Multi-Node), Helm v3.17.0, containerd 2.3.1, Docker 29.8"),
        ("Namespaces", "devops-lab6 (Declarative Stack) & devops-lab6-helm (Helm Release Stack)"),
        ("Verification Outcome", "13 / 13 End-to-End Automated Tests Passed (100% SUCCESS)")
    ]
    for i, (k, v) in enumerate(meta_data):
        cell_k, cell_v = tbl_meta.cell(i, 0), tbl_meta.cell(i, 1)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)
        set_cell_background(cell_k, "F1F5F9")
        set_cell_background(cell_v, "FFFFFF")
        set_cell_margins(cell_k, 60, 60, 100, 100)
        set_cell_margins(cell_v, 60, 60, 100, 100)
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_before = Pt(1)
        pk.paragraph_format.space_after = Pt(1)
        rk = pk.add_run(k)
        rk.font.name = "Calibri"
        rk.font.size = Pt(9.5)
        rk.font.bold = True
        rk.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_before = Pt(1)
        pv.paragraph_format.space_after = Pt(1)
        rv = pv.add_run(v)
        rv.font.name = "Calibri"
        rv.font.size = Pt(9.5)
        rv.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    set_table_borders(tbl_meta, "CBD5E1")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1. Executive Summary & Lab Objectives
    h1 = doc.add_heading(level=1)
    r = h1.add_run("1. Executive Summary & Laboratory Objectives")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The primary objective of this laboratory is to master advanced Kubernetes workload paradigms beyond long-running deployments, implement production-grade configuration externalization, enforce zero-trust secret protection, and package microservices into parameterizable, version-controlled Helm charts. The laboratory establishes deep hands-on proficiency across five core pillars:")

    objectives = [
        ("Batch Job Primitives (batch/v1)", "Architecting finite, run-to-completion workloads with explicit completion quotas, concurrent worker parallelism, exponential failure backoff limits, and active execution deadlines."),
        ("Scheduled CronJobs (batch/v1)", "Implementing automated periodic operations (e.g. cache eviction, audit compaction, health heartbeats) using POSIX cron expressions, concurrency policies (Forbid, Allow, Replace), and history retention limits."),
        ("Decoupled ConfigMaps (v1)", "Separating configuration artifacts from container binaries to satisfy 12-factor cloud-native principles, injecting settings via environment variables and live volume mounts."),
        ("Encrypted Secrets (v1/Opaque)", "Securing database credentials, cryptographic keys, and API bearer tokens using Base64 encryption, restricted filesystem permissions (mode 0400), and zero-trust masking patterns."),
        ("Helm 3 Packaging & Lifecycle", "Authoring an enterprise-grade Helm chart (Chart.yaml, values.yaml, templates), executing package creation, namespace-isolated deployment, atomic release upgrades, and instant rollbacks.")
    ]
    for title, desc in objectives:
        p_obj = doc.add_paragraph(style='List Bullet')
        p_obj.paragraph_format.space_before = Pt(2)
        p_obj.paragraph_format.space_after = Pt(3)
        r_b = p_obj.add_run(f"{title}: ")
        r_b.font.bold = True
        r_b.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
        p_obj.add_run(desc)

    add_callout(doc, "Unlike stateless Deployments designed to run indefinitely (restartPolicy: Always), Kubernetes Jobs represent batch processes that must run to completion and exit cleanly with code 0 (restartPolicy: OnFailure or Never). Helm 3 manages the entire lifecycle client-side, persisting state in Kubernetes Secrets.", "CORE PRINCIPLE")

    # 2. System Architecture & Topology
    h1 = doc.add_heading(level=1)
    r = h1.add_run("2. System Architecture & Multi-Node Cluster Topology")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The experimental infrastructure was established on a multi-node Kubernetes cluster orchestrated through containerd 2.3.1 and Docker Desktop. Workloads are distributed across control-plane and heterogeneous worker nodes with dual namespaces:")

    add_code_block(doc, """+---------------------------------------------------------------------------------------------------+
|                         KUBERNETES MULTI-NODE CLUSTER (v1.36.1)                                   |
|                                                                                                   |
|  +--------------------------------+   +--------------------------------------------------------+  |
|  |     NAMESPACE: devops-lab6     |   |              NAMESPACE: devops-lab6-helm               |  |
|  |  (Declarative Raw Stack)       |   |              (Helm 3 Release: lab6-release)           |  |
|  |                                |   |                                                        |  |
|  |  +--------------------------+  |   |  +--------------------------+  +--------------------+  |  |
|  |  | ConfigMap: devops-lab6   |  |   |  | ConfigMap: lab6-config   |  | Helm Secret: v1-v3 |  |  |
|  |  | Secret:    devops-lab6   |  |   |  | Secret:    lab6-secret   |  | (sh.helm.release)  |  |  |
|  |  +--------------------------+  |   |  +--------------------------+  +--------------------+  |  |
|  |             |                  |   |             |                                          |  |
|  |      +------+------+           |   |      +------+------+                                   |  |
|  |      |             |           |   |      |             |                                   |  |
|  |      v             v           |   |      v             v                                   |  |
|  | +----------+ +---------------+ |   | +----------+ +---------------+                         |  |
|  | |Deployment| |  batch/v1 Job | |   | |Deployment| |  batch/v1 Job |                         |  |
|  | | 2 Pods   | | 3 Completions | |   | | 2 Replicas| | 3 Completions |                        |  |
|  | | (Web UI) | | 2 Concurrent  | |   | | (Web UI) | | 2 Concurrent  |                         |  |
|  | +----------+ +---------------+ |   | +----------+ +---------------+                         |  |
|  |      |             |           |   |      |             |                                   |  |
|  |      v             v           |   |      v             v                                   |  |
|  | +----------+ +---------------+ |   | +----------+ +---------------+                         |  |
|  | | NodePort | |CronJob: Periodic|   | | NodePort | |CronJob: Periodic|                       |  |
|  | |  30086   | | Cleaner */2   | |   | |  30087   | | Cleaner */2   |                         |  |
|  | +----------+ +---------------+ |   | +----------+ +---------------+                         |  |
|  +--------------------------------+   +--------------------------------------------------------+  |
|                                                                                                   |
|  Scheduled Across: desktop-control-plane (172.21.0.6) | desktop-worker (172.21.0.4)                |
|                    desktop-worker2 (172.21.0.5)                                                   |
+---------------------------------------------------------------------------------------------------+""")

    # 3. Declarative Resource Manifests
    h1 = doc.add_heading(level=1)
    r = h1.add_run("3. Declarative Kubernetes Manifests Specification")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The complete declarative stack is organized into individual, decoupled YAML manifests adhering to standard Kubernetes API schemas:")

    manifests = [
        ("00-namespace.yaml", "v1/Namespace", "Defines the devops-lab6 namespace for logical workload boundary isolation."),
        ("01-configmap.yaml", "v1/ConfigMap", "Stores application environment variables (APP_ENV, LOG_LEVEL, MAX_BATCH_SIZE) and mounts app_settings.json as a volume."),
        ("02-secret.yaml", "v1/Secret (Opaque)", "Secures database user credentials, database passwords, API tokens, and vault encryption keys (0400 permissions)."),
        ("03-deployment.yaml", "apps/v1/Deployment", "Deploys 2 replicas of lab6-microservice:v1.0.0 with readiness/liveness probes, Downward API, and volume mounts."),
        ("04-service.yaml", "v1/Service (NodePort)", "Exposes the web dashboard on port 80 internally and nodePort 30086 externally."),
        ("05-job-data-processor.yaml", "batch/v1/Job", "Configures parallel batch data processing with completions: 3, parallelism: 2, backoffLimit: 4, and restartPolicy: OnFailure."),
        ("06-cronjob-periodic-cleaner.yaml", "batch/v1/CronJob", "Schedules maintenance tasks every 2 minutes (*/2 * * * *) with concurrencyPolicy: Forbid and history retention.")
    ]
    for fn, api, desc in manifests:
        p_m = doc.add_paragraph(style='List Bullet')
        p_m.paragraph_format.space_before = Pt(2)
        p_m.paragraph_format.space_after = Pt(2)
        r_fn = p_m.add_run(f"{fn} ({api}): ")
        r_fn.font.bold = True
        r_fn.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        p_m.add_run(desc)

    # 4. Helm Chart Engineering
    h1 = doc.add_heading(level=1)
    r = h1.add_run("4. Helm 3 Chart Engineering & Architecture")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The entire application stack was packaged into a reusable, parameterizable Helm 3 chart in helm/devops-lab6/. Key architectural files include:")

    helm_files = [
        ("Chart.yaml", "Chart metadata specifying apiVersion: v2, name: devops-lab6, version: 0.1.0, and appVersion: 1.0.0."),
        ("values.yaml", "Central configuration dictionary defining defaults for replicaCount, image repository/tag, service ports, ConfigMap parameters, Secret keys, and Job/CronJob toggles."),
        ("templates/_helpers.tpl", "Go template helper definitions providing standardized name truncation, full release naming, and common Kubernetes labels."),
        ("templates/deployment.yaml", "Parameterized deployment template utilizing values interpolation, Sprig functions, and volume mounts."),
        ("templates/job.yaml & cronjob.yaml", "Conditional templating ({{- if .Values.job.enabled }}) enabling dynamic batch workload inclusion."),
        ("templates/NOTES.txt", "Automated post-installation operational instructions output to the terminal upon deployment.")
    ]
    for fn, desc in helm_files:
        p_h = doc.add_paragraph(style='List Bullet')
        p_h.paragraph_format.space_before = Pt(2)
        p_h.paragraph_format.space_after = Pt(2)
        r_fn = p_h.add_run(f"{fn}: ")
        r_fn.font.bold = True
        r_fn.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        p_h.add_run(desc)

    # 5. Experimental Verification & Visual Evidence
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Experimental Execution & Verification Walkthrough")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The following subsections present high-resolution visual evidence and technical analysis of all execution milestones captured during the laboratory session:")

    # Milestone 1: Cluster Nodes
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.1 Cluster Health & Multi-Node Topology")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Verification of the 3-node Kubernetes cluster running Kubernetes v1.36.1 and containerd 2.3.1. Active namespaces devops-lab6 and devops-lab6-helm demonstrate proper boundary isolation.")
    add_figure(doc, "screenshot_cluster_nodes.png", "Figure 5.1: Multi-node cluster topology and active namespaces verification.")

    # Milestone 2: ConfigMaps & Secrets
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.2 ConfigMap & Zero-Trust Secret Ingestion Verification")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Inspection of pod environment variables and volume mounts. Environment variables APP_ENV, LOG_LEVEL, DB_USER, DB_PASSWORD, and API_AUTH_TOKEN were successfully injected. The mounted file /etc/secrets/vault_key.txt was verified with strict read-only permissions (0400).")
    add_figure(doc, "screenshot_configmap_secret.png", "Figure 5.2: Injected environment variables and volume-mounted configuration & secret files.")

    # Milestone 3: Batch Job
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.3 Parallel Batch Job Execution & Pod Completions")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Execution of data-batch-processor-job. The job successfully spawned parallel pods, executed batch partitions, performed cryptographic checksum verification, and attained Complete status (3/3 completions in 22 seconds) with clean exit code 0.")
    add_figure(doc, "screenshot_batch_job.png", "Figure 5.3: Batch job parallel pod scheduling, progress tracking, and execution telemetry.")

    # Milestone 4: CronJob
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.4 Scheduled CronJob Execution & Concurrency Control")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Inspection of system-periodic-cleaner-cron configured with POSIX schedule */2 * * * * and concurrencyPolicy: Forbid. On-demand job execution confirmed automated cache purging and monitoring telemetry emission.")
    add_figure(doc, "screenshot_cronjob.png", "Figure 5.4: CronJob specification, active schedule, and maintenance pod logs.")

    # Milestone 5: Helm Lifecycle
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.5 Helm 3 Packaging, Deployment, Upgrade & Rollback")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Complete demonstration of the Helm 3 application lifecycle: chart packaging (devops-lab6-0.1.0.tgz), release installation (Revision 1), atomic upgrade to 4 replicas with LOG_LEVEL=DEBUG (Revision 2), and instantaneous rollback back to Revision 1 (Revision 3: Rollback to 1).")
    add_figure(doc, "screenshot_helm_lifecycle.png", "Figure 5.5: Helm chart packaging, release installation, upgrade, rollback, and revision history.")

    # Milestone 6: Web Dashboard
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.6 Microservice Web Dashboard UI")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Live browser render of the microservice dashboard displaying pod topology, ConfigMap parameters, zero-trust masked secrets with SHA256 fingerprints, batch job specifications, and Helm metadata.")
    add_figure(doc, "screenshot_web_ui.png", "Figure 5.6: Interactive microservice web dashboard showing configuration, secrets, and telemetry.")

    # Milestone 7: Automated Test Suite
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("5.7 Automated End-to-End Verification Test Suite")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Execution output of scripts/verify_all.ps1 validating all 13 automated checks spanning nodes, namespaces, ConfigMaps, Secrets, deployments, services, batch jobs, cronjobs, and Helm release revisions.")
    add_figure(doc, "screenshot_verification_suite.png", "Figure 5.7: Automated verification test suite executing 13 checks with 100% pass rate.")

    # 6. Technical Comparison Matrices
    h1 = doc.add_heading(level=1)
    r = h1.add_run("6. Technical Comparison Matrices")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("The following matrices synthesize fundamental architectural differences across Kubernetes workloads and configuration mechanisms:")

    # Table 1: Workload Comparison
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("6.1 Workload Paradigms: Deployment vs Job vs CronJob")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    tbl_work = doc.add_table(rows=6, cols=4)
    tbl_work.alignment = WD_TABLE_ALIGNMENT.CENTER
    work_headers = ["Attribute", "Deployment (apps/v1)", "Job (batch/v1)", "CronJob (batch/v1)"]
    for j, h in enumerate(work_headers):
        c = tbl_work.cell(0, j)
        set_cell_background(c, "1E293B")
        set_cell_margins(c, 80, 80, 100, 100)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)

    work_rows = [
        ("Primary Purpose", "Continuous long-running microservices / APIs", "Finite, run-to-completion batch tasks", "Periodic, scheduled automated workloads"),
        ("Lifecycle & Restart", "Always restarts pods (restartPolicy: Always)", "Terminates on success (OnFailure / Never)", "Instantiates Jobs based on cron expression"),
        ("Scaling Semantics", "Replicas count maintained indefinitely", "Completions & Parallelism quotas", "Manages active jobs per concurrency policy"),
        ("Failure Handling", "Replaces unhealthy pods automatically", "Exponential backoff retry (backoffLimit)", "Failed history limit + starting deadlines"),
        ("Typical Use Case", "Web frontend, REST API, ingress gateways", "Database migrations, ETL pipelines, reports", "Nightly backups, cache eviction, audits")
    ]
    for i, row in enumerate(work_rows):
        for j, val in enumerate(row):
            c = tbl_work.cell(i + 1, j)
            set_cell_background(c, "F8FAFC" if i % 2 == 0 else "FFFFFF")
            set_cell_margins(c, 60, 60, 100, 100)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if j == 0:
                r.font.bold = True
    set_table_borders(tbl_work, "CBD5E1")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Table 2: ConfigMap vs Secret
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("6.2 Configuration Decoupling: ConfigMap vs Secret")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    tbl_cfg = doc.add_table(rows=6, cols=3)
    tbl_cfg.alignment = WD_TABLE_ALIGNMENT.CENTER
    cfg_headers = ["Attribute", "ConfigMap (v1)", "Secret (v1/Opaque)"]
    for j, h in enumerate(cfg_headers):
        c = tbl_cfg.cell(0, j)
        set_cell_background(c, "1E293B")
        set_cell_margins(c, 80, 80, 100, 100)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)

    cfg_rows = [
        ("Storage Encoding", "Plaintext UTF-8 string keys & values", "Base64 encoded binary/string values"),
        ("Primary Target", "Non-confidential app settings, config files", "Passwords, API tokens, TLS private keys"),
        ("Etcd Security", "Stored unencrypted in etcd by default", "Can be encrypted at rest via KMS provider"),
        ("Filesystem Permissions", "Standard volume mount default permissions", "Strict permission masking (defaultMode: 0400)"),
        ("Consumption Vectors", "env, envFrom: configMapRef, volumeMounts", "env, envFrom: secretRef, volumeMounts")
    ]
    for i, row in enumerate(cfg_rows):
        for j, val in enumerate(row):
            c = tbl_cfg.cell(i + 1, j)
            set_cell_background(c, "F8FAFC" if i % 2 == 0 else "FFFFFF")
            set_cell_margins(c, 60, 60, 100, 100)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if j == 0:
                r.font.bold = True
    set_table_borders(tbl_cfg, "CBD5E1")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Table 3: Raw K8s vs Helm
    h2 = doc.add_heading(level=2)
    r2 = h2.add_run("6.3 Manifest Management: Raw Kubernetes vs Helm 3")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    tbl_helm = doc.add_table(rows=6, cols=3)
    tbl_helm.alignment = WD_TABLE_ALIGNMENT.CENTER
    helm_headers = ["Dimension", "Raw Kubernetes Manifests (kubectl)", "Helm 3 Package Manager"]
    for j, h in enumerate(helm_headers):
        c = tbl_helm.cell(0, j)
        set_cell_background(c, "1E293B")
        set_cell_margins(c, 80, 80, 100, 100)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)

    helm_rows = [
        ("Parameterization", "Static YAML files; requires sed or manual edits", "values.yaml with Go templating & Sprig logic"),
        ("Release Lifecycle", "Manual kubectl apply/delete across files", "Atomic install, upgrade, and rollback commands"),
        ("Version History", "Limited to Deployment ReplicaSet revisions", "Complete release revision history in Secrets"),
        ("Environment Parity", "Requires duplicate manifests per environment", "Single chart with dev/prod values files"),
        ("Package Sharing", "Shared via raw Git repositories or directories", "Packaged as .tgz archives and OCI registries")
    ]
    for i, row in enumerate(helm_rows):
        for j, val in enumerate(row):
            c = tbl_helm.cell(i + 1, j)
            set_cell_background(c, "F8FAFC" if i % 2 == 0 else "FFFFFF")
            set_cell_margins(c, 60, 60, 100, 100)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if j == 0:
                r.font.bold = True
    set_table_borders(tbl_helm, "CBD5E1")

    # 7. Comprehensive Viva Voce Questions & Answers
    h1 = doc.add_heading(level=1)
    r = h1.add_run("7. Comprehensive Lab Viva & Technical Interview Q&A")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The following 15 high-yield questions provide exhaustive theoretical and practical preparation for laboratory viva examinations and technical DevOps interviews:")

    viva_qa = [
        ("Q1: What is the fundamental difference between a Pod managed by a Deployment versus a Pod managed by a Job?",
         "A Deployment manages long-running, continuous processes (e.g. web servers, APIs) and guarantees that a specified number of replicas remain running indefinitely. If a pod exits with code 0 or fails, the Deployment ReplicaSet recreates it. Conversely, a Job manages run-to-completion batch workloads. It tracks pods until a designated number of completions succeed (exit code 0). Once finished, the Job does not restart the pods, preserving their logs and final status for auditability."),

        ("Q2: How do 'completions' and 'parallelism' interact in a Kubernetes Job specification?",
         "'completions' defines the total number of pods that must terminate successfully with exit code 0 for the entire Job to be marked Complete. 'parallelism' sets the upper limit on how many pods are allowed to run concurrently at any given instant. For example, completions: 3 and parallelism: 2 will execute 2 pods simultaneously; as soon as one completes, a third pod is instantiated to fulfill the completion quota."),

        ("Q3: What are the valid values for restartPolicy in a Job, and why is 'Always' forbidden?",
         "In a Job template, restartPolicy must be either 'OnFailure' or 'Never'. 'Always' is strictly forbidden because Jobs manage run-to-completion tasks. If restartPolicy were Always, the container would restart infinitely upon successful completion (code 0), preventing the Job from ever reaching its finished state. Under 'OnFailure', a failed container restarts inside the same pod; under 'Never', a failed container leaves the pod in Failed state and the Job controller spawns a replacement pod."),

        ("Q4: What is the purpose of 'backoffLimit' and how does exponential backoff work in Jobs?",
         "'backoffLimit' defines the maximum number of retries before the Job controller marks the entire Job as Failed. When a pod fails, the controller retries with an exponential backoff delay (10s, 20s, 40s... up to a maximum of 6 minutes) to prevent thrashing the cluster or overwhelming degraded downstream resources."),

        ("Q5: What are the three CronJob concurrencyPolicy options, and what are their production implications?",
         "The concurrencyPolicy specifies how to handle concurrent executions of a Job created by a CronJob:\n1. 'Allow' (default): Concurrent jobs are allowed to run concurrently. Risk: Resource contention or race conditions if jobs take longer than the schedule.\n2. 'Forbid': If previous job execution has not finished, the new scheduled run is skipped. Recommended for ETL and backup jobs to prevent data corruption.\n3. 'Replace': If previous job is still running, it is immediately canceled and replaced by the new job."),

        ("Q6: How does Kubernetes handle CronJob missed schedules via 'startingDeadlineSeconds'?",
         "If a CronJob fails to instantiate at its scheduled time (due to cluster downtime, API server saturation, or resource quotas), 'startingDeadlineSeconds' specifies the maximum allowable delay (in seconds) during which the job can still start. If the delay exceeds this window, the scheduled run is counted as a miss and dropped until the next cron interval."),

        ("Q7: How are ConfigMaps updated inside running Pods when consumed via volume mounts versus environment variables?",
         "When a ConfigMap is mounted as a volume (/etc/config), the local kubelet periodically polls the API server and automatically updates the projected files inside the pod without requiring a pod restart (dynamic sync). Conversely, when ConfigMap keys are injected as environment variables (env / envFrom), environment variables are bound during container initialization and NEVER update dynamically without recreating the pod."),

        ("Q8: Why are Kubernetes Secrets stored as Base64 encoded strings, and does Base64 provide encryption?",
         "Base64 is strictly an encoding mechanism, NOT encryption. It encodes binary data (e.g. certificates, private keys) into ASCII text suitable for serialization inside JSON/YAML manifests. To achieve genuine security, Kubernetes Secrets must be encrypted at rest in etcd using KMS (Key Management Service) providers, protected via RBAC, and restricted using read-only filesystem volume mounts with mode 0400."),

        ("Q9: What is the benefit of using 'stringData' over 'data' when writing Kubernetes Secret manifests?",
         "'stringData' allows developers to write plaintext strings directly in declarative YAML manifests without manually pre-encoding them using 'echo -n | base64'. Upon receiving the manifest, the Kubernetes API server automatically converts stringData values into Base64-encoded 'data' entries before storing them in etcd."),

        ("Q10: What is the Downward API, and how was it leveraged in Lab 6?",
         "The Downward API allows container processes to consume metadata about themselves and the cluster without calling the Kubernetes API server directly. In Lab 6, fieldRef was used to inject metadata.name (POD_NAME), metadata.namespace (POD_NAMESPACE), status.podIP (POD_IP), and spec.nodeName (NODE_NAME) as environment variables into the application containers."),

        ("Q11: How does Helm 3 differ architecturally from Helm 2?",
         "The primary architectural change in Helm 3 was the complete removal of 'Tiller' (the server-side component of Helm 2). Helm 3 operates as a client-only binary that communicates directly with the Kubernetes API server using the user's kubeconfig credentials and RBAC permissions. Furthermore, release metadata in Helm 3 is stored directly as Kubernetes Secrets in the target release namespace rather than in kube-system ConfigMaps."),

        ("Q12: What is the three-way merge patch strategy used by Helm during upgrades?",
         "During a 'helm upgrade', Helm computes a three-way merge patch considering:\n1. The old manifest from the previous release,\n2. The live state of the resources currently running in the cluster,\n3. The new manifest generated by the upgraded chart.\nThis prevents Helm from overwriting out-of-band modifications (such as horizontal autoscalers dynamically adjusting replica counts)."),

        ("Q13: How does 'helm rollback' restore an application to a previous state?",
         "When 'helm rollback <release> <revision>' is executed, Helm retrieves the release state manifest stored in the historical Secret of that revision, generates a new release revision (e.g. Revision 3 = Rollback to 1), and applies the delta to the cluster. Deployments, ConfigMaps, and Secrets are restored atomically without downtime."),

        ("Q14: What is the function of the 'templates/_helpers.tpl' file in a Helm chart?",
         "'_helpers.tpl' defines reusable Go template partials and named templates using {{- define 'name' -}} blocks. These helpers standardize naming conventions (e.g. truncating release names to 63 characters to satisfy DNS-1123 label constraints) and generate unified metadata labels across all chart resources."),

        ("Q15: How does Helm track releases, and where can release records be inspected directly?",
         "Helm tracks releases as Kubernetes Secrets in the namespace where the release was deployed, named according to the pattern 'sh.helm.release.v1.<release-name>.v<revision>'. These secrets contain compressed, Base64-encoded release metadata including the full rendered manifest, values, and status.")
    ]
    for q, a in viva_qa:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(6)
        p_q.paragraph_format.space_after = Pt(2)
        rq = p_q.add_run(q)
        rq.font.bold = True
        rq.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0)
        p_a.paragraph_format.space_after = Pt(4)
        p_a.paragraph_format.line_spacing = 1.15
        p_a.add_run(a)

    # 8. Operational Runbook & Troubleshooting
    h1 = doc.add_heading(level=1)
    r = h1.add_run("8. Production Operational Runbook & Troubleshooting")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("Practical troubleshooting commands for diagnostic investigations in production Kubernetes environments:")

    runbook_steps = [
        ("Inspecting Job Failure Logs", "kubectl describe job <job-name> -n <ns>; kubectl logs -l batch.kubernetes.io/job-name=<job-name> --tail=100"),
        ("Manually Triggering CronJob Execution", "kubectl create job --from=cronjob/<cronjob-name> manual-debug-run -n <ns>"),
        ("Inspecting Raw Secret Data", "kubectl get secret <secret-name> -n <ns> -o jsonpath='{.data.<key>}' | base64 --decode"),
        ("Validating Helm Chart Rendering", "helm lint <chart-path>; helm template <release-name> <chart-path> --debug"),
        ("Debugging Stuck Helm Releases", "helm history <release-name> -n <ns>; helm rollback <release-name> <previous-rev> -n <ns>"),
        ("Forcing Job Termination / Clean up", "kubectl delete job <job-name> -n <ns> --cascade=foreground")
    ]
    for action, cmd in runbook_steps:
        p_rb = doc.add_paragraph(style='List Bullet')
        p_rb.paragraph_format.space_before = Pt(2)
        p_rb.paragraph_format.space_after = Pt(2)
        r_a = p_rb.add_run(f"{action}: ")
        r_a.font.bold = True
        r_a.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        r_c = p_rb.add_run(cmd)
        r_c.font.name = "Consolas"
        r_c.font.size = Pt(9.5)
        r_c.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    # Conclusion & Sign-off
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.line_spacing = 1.15
    p_concl.add_run("Conclusion: DevOps Laboratory 6 was completed with 100% verification across all test metrics. Declarative Jobs and CronJobs, ConfigMap and Secret ingestion, and Helm 3 lifecycle management were successfully orchestrated and documented in compliance with CHRIST (Deemed to be University) academic and engineering standards.")

    output_filename = "Lab6_Kubernetes_Jobs_Config_Helm_Report.docx"
    doc.save(output_filename)
    print(f"Report successfully compiled and saved to {output_filename}!")

if __name__ == '__main__':
    build_docx()
