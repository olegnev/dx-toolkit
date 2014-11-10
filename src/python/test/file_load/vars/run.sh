main() {
    dx-download-all-inputs

    # compare the bash variables to the old version of the code
    dx-print-bash-vars --dbg-compare-old > BASH_VAR_ERRS

    ## Checking file type
    check_var_defined "$seq1"

    check_var_defined "$seq2"

    ## Checking array:file type
    check_array_defined "$genes"

    check_var_defined "$seq1_name" "A.txt"
    check_var_defined "$seq1_path" "\$HOME/in/seq1/A.txt"
    check_var_defined "$seq1_prefix" "A"
    check_var_defined "$seq2_name" "A.txt"
    check_var_defined "$seq2_path" "\$HOME/in/seq2/A.txt"
    check_var_defined "$seq2_prefix" "A"

    rc=( A.txt A.txt )
    check_string_array "genes_name" genes_name[@] rc[@]

    rc=( \$HOME/in/genes/0/A.txt \$HOME/in/genes/1/A.txt )
    check_string_array "genes_path" genes_path[@] rc[@]

    rc=( A A )
    check_string_array "genes_prefix" genes_prefix[@] rc[@]

    dx-upload-all-outputs
}

# Check if an environment variable is defined, and if it has the correct value
check_var_defined() {
    if [[ -z $1 ]];
    then
        echo "Error: expecting environment variable $1 to be defined"
        dx-jobutil-report-error "Error: expecting environment variable $1 to be defined" "AppError"
        exit 1
    fi

    if [ $# -ne 2 ];
    then
        return
    fi

    if [[ ! "$1" == "$2" ]];
    then
        echo "Error: expecting environment variable $1 to equal $2"
        dx-jobutil-report-error "Error: expecting environment variable $1 to equal $2" "AppError"
        exit 1
    fi
}

check_array_defined() {
    if [[ $# -ne 1 ]];
    then
        echo "Error: should call check_array_defined with one argument"
        dx-jobutil-report-error "should call check_array_defined with one argument"
        exit 1
    fi
    if [[ -z $1 ]];
    then
        echo "Error: expecting environment variable $1 to be defined"
        dx-jobutil-report-error "expecting environment variable $1 to be defined" "AppError"
        exit 1
    fi
}

check_string_array() {
    if [[ $# -ne 3 ]];
    then
        echo "Error: check_string_array expects three inputs, but got $#"
        dx-jobutil-report-error "check_string_array expects three inputs, but got $#" "AppError"
        exit 1
    fi

    #echo "num args=$#"
    declare -a a=("${!2}")
    declare -a b=("${!3}")

    local len_a=${#a[@]}
    local len_b=${#b[@]}
    a_str=${a[@]}
    b_str=${b[@]}

    if [ $len_a -ne $len_b ];
    then
        echo "Error: length mismatch, var=$1  $a_str != $b_str"
        dx-jobutil-report-error "length mismatch, var=$1  $a_str != $b_str"
        exit 1
    fi

    for (( i=0; i<${len_a}; i++ ));
    do
        if [ ${a[$i]} != ${b[$i]} ];
        then
            echo "Error: mismatch in values for var=$1  $a_str != $b_str"
            dx-jobutil-report-error "Error: mismatch in values for var=$1  $a_str != $b_str"
            exit 1
        fi
    done
}
