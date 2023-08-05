echo Step 1 - Create a work directory::

mkdir workdir
cd workdir


echo Step 2 - Gather a reference fasta file::

    # For this example we will use a fasta file from our sister project, snp-pipeline
wget https://raw.githubusercontent.com/CFSAN-Biostatistics/snp-pipeline/master/snppipeline/data/agonaInputs/reference/NC_011149.fasta

echo Step 3 - Generate the mutated sequences::

    # The mutated sequence files are generated in the current working directory
snpmutator.py -r 1 -n 2 -s 2 -i 0 -d 0 -o summary NC_011149.fasta

echo Step 4 - Examine the results::

head NC_011149_mutated_*.fasta
cat summary
