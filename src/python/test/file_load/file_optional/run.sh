main() {
    dx-download-all-inputs

    mkdir -p out/seq2

    if [ -n "$create_seq3" ]
    then
        mkdir -p out/seq3
        echo "abcd" > out/seq3/X.txt
    fi

    dx-upload-all-outputs
}
