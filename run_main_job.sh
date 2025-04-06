#!/bin/bash
#SBATCH --job-name=run_main
#SBATCH --output=main_output_%j.out
#SBATCH --error=main_error_%j.err
#SBATCH --partition=k2-hipri
#SBATCH --time=3:00:00
#SBATCH --qos=normal
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G

# Load Python module
module load python3/3.10.5/gcc-9.3.0

# Update PATH and PYTHONPATH for user-level pip packages
export PATH=$HOME/.local/bin:$PATH
export PYTHONPATH=$HOME/.local/lib/python3.10/site-packages:$PYTHONPATH

# Move to your project directory
cd $HOME/java_repositories_commit_data

# Required Python packages
REQUIRED_PKGS=("psutil" "gitpython")

for pkg in "${REQUIRED_PKGS[@]}"; do
    if ! python3 -c "import $pkg" &> /dev/null; then
        echo "📦 Installing missing module: $pkg"
        pip install --user $pkg
    else
        echo "✅ Module $pkg already installed"
    fi
done

# Run the main Python script
echo "🚀 Running main.py ..."
python3 main.py
echo "✅ Done."
