main() {
    dx-download-all-inputs

    check_var_defined "dx_seq1"
    check_var_defined "dx_seq2"
    check_var_defined "dx_genes"

    dx-upload-all-outputs
}

# Check if an environment variable is defined
function check_var_defined {
    varname=$1
    if [ -n "$varname" ]
        echo "Error: expecting environment variable $varname to be defined"
        exit 1
    fi
}
