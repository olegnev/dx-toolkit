main() {
    dx-download-all-inputs

    gene_d="out/genes"
    mkdir -p $gene_d
    echo 'ABCD' > $gene_d/A.txt
    echo '1234' > $gene_d/B.txt

    # create a few subdirectories with data
    mkdir -p $gene_d/clue
    echo "ABC" > $gene_d/clue/X_1.txt
    for i in 2 3; do
        cp $gene_d/clue/X_1.txt $gene_d/clue/X_$i.txt
    done
    cp -r $gene_d/clue $gene_d/hint

    # another subdirectory
    phen_d="out/phenotypes"
    mkdir -p $phen_d
    echo 'hello world' > $phen_d/C.txt

    mkdir -p $phen_d/clue2
    echo "ACGT" > $phen_d/clue2/Y_1.txt
    for i in 2 3; do
        cp $phen_d/clue2/Y_1.txt $phen_d/clue2/Y_$i.txt
    done
    cp -r $phen_d/clue2 $phen_d/hint2

    dx-upload-all-outputs
}
