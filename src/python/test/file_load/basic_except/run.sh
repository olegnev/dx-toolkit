main() {
    dx-download-all-inputs --except seq1 --except seq2

    # Check file content
    dx download "$seq1" -o seq1
    dx download "$seq2" -o seq2

    mkdir -p out/result
    echo "hello world, $seq1, $seq2" > out/result/report.txt

    mkdir -p out/genes
    echo 'ls in/$ref' > out/genes/refs_ls.txt
    echo 'ls in/$reads' > out/genes/reads_ls.txt

    dx-upload-all-outputs --except genes
}
