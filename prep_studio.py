import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import glob

class ORCAPrepStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ORCA Prep Studio - PyChemTools")
        self.geometry("640x880")
        
        # State variables
        self.mode = None # "single" or "batch"
        self.filename = ""
        self.xyz_lines = []
        self.batch_files = []
        
        self.create_widgets()

    def create_widgets(self):
        # 1. File Selection Frame
        frame_file = ttk.LabelFrame(self, text="1. Input Selection (.xyz)")
        frame_file.pack(fill="x", padx=10, pady=5)
        
        self.lbl_file = ttk.Label(frame_file, text="No file or folder loaded.", foreground="red")
        self.lbl_file.pack(side="left", padx=10, pady=10)
        
        btn_batch = ttk.Button(frame_file, text="Batch Folder", command=self.load_folder)
        btn_batch.pack(side="right", padx=5, pady=10)
        
        btn_browse = ttk.Button(frame_file, text="Single XYZ", command=self.load_xyz)
        btn_browse.pack(side="right", padx=5, pady=10)

        # 2. Molecular Properties
        frame_mol = ttk.LabelFrame(self, text="2. Molecular Properties")
        frame_mol.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_mol, text="Charge:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.var_charge = tk.IntVar(value=0)
        ttk.Spinbox(frame_mol, from_=-5, to=5, textvariable=self.var_charge, width=5).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_mol, text="Multiplicity:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.var_mult = tk.IntVar(value=1)
        ttk.Spinbox(frame_mol, from_=1, to=7, textvariable=self.var_mult, width=5).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # 3. Calculation Setup
        frame_calc = ttk.LabelFrame(self, text="3. Calculation Setup")
        frame_calc.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_calc, text="Job Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cb_job = ttk.Combobox(frame_calc, values=["SP", "Opt", "Opt Freq", "Freq", "OptTS Freq"], state="readonly")
        self.cb_job.current(1)
        self.cb_job.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_calc, text="Method:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.cb_method = ttk.Combobox(frame_calc, values=["B3LYP", "PBE0", "wB97X-D4", "M06-2X", "BP86", "HF"], state="readonly")
        self.cb_method.current(0)
        self.cb_method.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_calc, text="Basis Set:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.cb_basis = ttk.Combobox(frame_calc, values=["def2-SVP", "def2-TZVP", "def2-TZVPP", "6-31G(d)"], state="readonly")
        self.cb_basis.current(0)
        self.cb_basis.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(frame_calc, text="Dispersion:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.cb_disp = ttk.Combobox(frame_calc, values=["None", "D3ZERO", "D3BJ", "D4"], state="readonly")
        self.cb_disp.current(2)
        self.cb_disp.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_calc, text="Solvation:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.cb_solv = ttk.Combobox(frame_calc, values=["None", "CPCM(Water)", "CPCM(CH2Cl2)", "SMD"], state="readonly")
        self.cb_solv.current(0)
        self.cb_solv.grid(row=2, column=3, padx=5, pady=5)

        # 4. Resources
        frame_res = ttk.LabelFrame(self, text="4. Resources")
        frame_res.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_res, text="Cores (MPI):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.var_cores = tk.IntVar(value=16)
        ttk.Spinbox(frame_res, from_=1, to=128, textvariable=self.var_cores, width=5).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_res, text="MaxCore (MB/core):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.var_memory = tk.IntVar(value=4000)
        ttk.Entry(frame_res, textvariable=self.var_memory, width=10).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # 5. HPC Submission
        frame_hpc = ttk.LabelFrame(self, text="5. HPC Submission Generation")
        frame_hpc.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_hpc, text="Manager:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cb_hpc = ttk.Combobox(frame_hpc, values=["None", "SLURM", "PBS"], state="readonly")
        self.cb_hpc.current(1)
        self.cb_hpc.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_hpc, text="Queue/Partition:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.var_queue = tk.StringVar(value="standard")
        ttk.Entry(frame_hpc, textvariable=self.var_queue, width=15).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(frame_hpc, text="Walltime:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.var_time = tk.StringVar(value="24:00:00")
        ttk.Entry(frame_hpc, textvariable=self.var_time, width=15).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_hpc, text="ORCA Executable Path (Optional):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.var_orca_path = tk.StringVar(value="orca")
        ttk.Entry(frame_hpc, textvariable=self.var_orca_path, width=15).grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # 6. Advanced Geometry & Constraints
        frame_adv = ttk.LabelFrame(self, text="6. Advanced Setup (Optional)")
        frame_adv.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_adv, text="Freeze Atoms (space or comma separated indices, e.g., 0 1 5):").pack(anchor="w", padx=5, pady=2)
        self.var_freeze = tk.StringVar()
        ttk.Entry(frame_adv, textvariable=self.var_freeze, width=60).pack(padx=5, pady=5, anchor="w")
        
        ttk.Label(frame_adv, text="Additional Simple Keywords (e.g., TightSCF, RIJCOSX):").pack(anchor="w", padx=5, pady=2)
        self.var_add = tk.StringVar()
        ttk.Entry(frame_adv, textvariable=self.var_add, width=60).pack(padx=5, pady=5, anchor="w")

        # 7. Action and Preview
        self.btn_gen = ttk.Button(self, text="Generate Inputs & Scripts", command=self.process_generation, state="disabled")
        self.btn_gen.pack(pady=10)
        
        ttk.Label(self, text="Output / Log Preview:").pack(anchor="w", padx=10)
        
        frame_text = tk.Frame(self)
        frame_text.pack(fill="both", expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(frame_text)
        scrollbar.pack(side="right", fill="y")
        self.text_preview = tk.Text(frame_text, height=10, yscrollcommand=scrollbar.set, bg="#f5f5f5")
        self.text_preview.pack(fill="both", expand=True)
        scrollbar.config(command=self.text_preview.yview)

    def load_xyz(self):
        path = filedialog.askopenfilename(title="Select XYZ File", filetypes=[("XYZ Files", "*.xyz")])
        if not path: return
            
        self.mode = "single"
        self.filename = path
        self.lbl_file.config(text=f"Single: {os.path.basename(path)}", foreground="green")
        
        with open(path, 'r') as f:
            raw_lines = f.readlines()
            
        if len(raw_lines) >= 3:
            try:
                num_atoms = int(raw_lines[0].strip())
                self.xyz_lines = raw_lines[2:2+num_atoms]
                self.btn_gen.config(text="Generate 1 Input Group", state="normal")
                self.update_preview(f"Successfully loaded {num_atoms} atoms.\nReady to generate.")
            except ValueError:
                messagebox.showerror("Error", "Invalid XYZ format.")
        else:
            messagebox.showerror("Error", "XYZ file is malformed.")

    def load_folder(self):
        path = filedialog.askdirectory(title="Select Folder with XYZ Files")
        if not path: return
        
        self.batch_files = glob.glob(os.path.join(path, "*.xyz"))
        if not self.batch_files:
            messagebox.showerror("Error", "No .xyz files found in the selected folder.")
            return
            
        self.mode = "batch"
        self.lbl_file.config(text=f"Batch: {len(self.batch_files)} files loaded", foreground="blue")
        self.btn_gen.config(text=f"Generate {len(self.batch_files)} Input Groups", state="normal")
        self.update_preview(f"Loaded {len(self.batch_files)} files from:\n{path}\n\nReady for batch generation.")

    def update_preview(self, text):
        self.text_preview.delete(1.0, tk.END)
        self.text_preview.insert(tk.END, text)

    def build_input_string(self, xyz_lines):
        lines = []
        kw_job = self.cb_job.get()
        kw_method = self.cb_method.get()
        kw_basis = self.cb_basis.get()
        kw_disp = self.cb_disp.get()
        kw_solv = self.cb_solv.get()
        kw_add = self.var_add.get().strip()
        
        simple_line = f"! {kw_method} {kw_basis} {kw_job}"
        if kw_disp != "None" and "D4" not in kw_method and "D3" not in kw_method:
            simple_line += f" {kw_disp}"
        if kw_solv != "None":
            simple_line += f" {kw_solv}"
        if kw_add:
            simple_line += f" {kw_add}"
            
        lines.extend([simple_line, ""])
        
        cores = self.var_cores.get()
        mem = self.var_memory.get()
        if cores > 1:
            lines.append(f"%pal nprocs {cores} end")
        lines.extend([f"%maxcore {mem}", ""])
        
        freeze_str = self.var_freeze.get().strip()
        if freeze_str:
            lines.extend(["%geom", "  Constraints"])
            indices = [int(part) for part in freeze_str.replace(',', ' ').split() if part.isdigit()]
            for idx in indices:
                lines.append(f"    {{ C {idx} C }}")
            lines.extend(["  end", "end", ""])
            
        charge = self.var_charge.get()
        mult = self.var_mult.get()
        lines.append(f"* xyz {charge} {mult}")
        for xyz in xyz_lines:
            lines.append(xyz.strip())
        lines.extend(["*", ""])
        
        return "\n".join(lines)

    def build_hpc_script(self, job_name):
        manager = self.cb_hpc.get()
        if manager == "None":
            return None
            
        cores = self.var_cores.get()
        queue = self.var_queue.get()
        walltime = self.var_time.get()
        orca_cmd = self.var_orca_path.get()
        
        lines = ["#!/bin/bash", ""]
        
        if manager == "SLURM":
            lines.extend([
                f"#SBATCH --job-name={job_name}",
                f"#SBATCH --partition={queue}",
                f"#SBATCH --nodes=1",
                f"#SBATCH --ntasks={cores}",
                f"#SBATCH --time={walltime}",
                "",
                "module load orca # Ensure your HPC module matches",
                f"{orca_cmd} {job_name}.inp > {job_name}.out"
            ])
        elif manager == "PBS":
            lines.extend([
                f"#PBS -N {job_name}",
                f"#PBS -q {queue}",
                f"#PBS -l nodes=1:ppn={cores}",
                f"#PBS -l walltime={walltime}",
                "",
                "cd $PBS_O_WORKDIR",
                "module load orca # Ensure your HPC module matches",
                f"{orca_cmd} {job_name}.inp > {job_name}.out"
            ])
            
        return "\n".join(lines)

    def process_generation(self):
        log = []
        success, fail = 0, 0
        manager = self.cb_hpc.get()
        
        files_to_process = [self.filename] if self.mode == "single" else self.batch_files
        generated_scripts = [] 
        
        target_dir = ""
        
        for file_path in files_to_process:
            try:
                # Read XYZ
                with open(file_path, 'r') as f:
                    raw = f.readlines()
                num_atoms = int(raw[0].strip())
                current_xyz = raw[2:2+num_atoms]
                
                job_name = os.path.splitext(os.path.basename(file_path))[0]
                dir_name = os.path.dirname(file_path)
                target_dir = dir_name 
                
                # Write .inp
                inp_str = self.build_input_string(current_xyz)
                inp_path = os.path.join(dir_name, f"{job_name}.inp")
                with open(inp_path, "w") as f:
                    f.write(inp_str)
                    
                # Write individual .sh (if requested)
                if manager != "None":
                    sh_str = self.build_hpc_script(job_name)
                    script_name = f"{job_name}.sh"
                    sh_path = os.path.join(dir_name, script_name)
                    with open(sh_path, "w") as f:
                        f.write(sh_str)
                    generated_scripts.append(script_name)
                    
                success += 1
                log.append(f"SUCCESS: {job_name}.inp" + (f" + .sh" if manager != "None" else ""))
                
            except Exception as e:
                fail += 1
                log.append(f"FAILED: {os.path.basename(file_path)} - {str(e)}")
        
        # --- Master Submission Script Generation ---
        master_msg = ""
        if self.mode == "batch" and manager != "None" and success > 0:
            submit_cmd = "sbatch" if manager == "SLURM" else "qsub"
            master_path = os.path.join(target_dir, "submit_all.sh")
            
            try:
                with open(master_path, "w") as f:
                    f.write("#!/bin/bash\n\n")
                    f.write(f"echo 'Submitting {len(generated_scripts)} jobs via {manager}...'\n\n")
                    
                    for script in generated_scripts:
                        f.write(f"{submit_cmd} {script}\n")
                        f.write("sleep 1  # Polite delay for the scheduler\n")
                        
                    f.write("\necho 'All jobs submitted successfully!'\n")
                
                try:
                    os.chmod(master_path, 0o755)
                except Exception:
                    pass
                    
                master_msg = f"\nSUCCESS: Master script created -> submit_all.sh"
            except Exception as e:
                master_msg = f"\nFAILED to create master script: {str(e)}"
        
        log_text = f"Generation Complete!\nSuccess: {success} | Failed: {fail}{master_msg}\n\n" + "\n".join(log)
        
        # If single, print the script preview
        if self.mode == "single" and manager != "None":
            job_name = os.path.splitext(os.path.basename(self.filename))[0]
            log_text += f"\n\n--- PREVIEW OF {job_name}.sh ---\n{self.build_hpc_script(job_name)}"
            
        self.update_preview(log_text)
        messagebox.showinfo("Complete", f"Generated {success} input groups.")

if __name__ == "__main__":
    app = ORCAPrepStudio()
    app.mainloop()