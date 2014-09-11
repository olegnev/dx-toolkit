main() {
#    dx-print-bash-vars

    dx-download-all-inputs
    
    check_var_defined "$seq1"
    check_var_defined "$seq2"
    check_var_defined "$genes"

#    mkdir -p out/foo
    dx-upload-all-outputs
}

# Check if an environment variable is defined
check_var_defined() {
    if [[ -z $1 ]]; 
    then
        echo "Error: expecting environment variable $1 to be defined"
        dx-jobutil-report-error "Error: expecting environment variable $1 to be defined" "AppError"
        exit 1
    fi
}


