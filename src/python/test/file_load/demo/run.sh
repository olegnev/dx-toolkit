main() {
    dx-download-all-inputs

    mkdir -p out/result
    cat in/seq1/* >> out/result/report.txt
    cat in/seq2/* >> out/result/report.txt

    dx-upload-all-outputs
}
