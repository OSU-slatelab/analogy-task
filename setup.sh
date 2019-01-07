#!/bin/bash
#
# Initial setup for running analogy task implementation
#
# Downloads dependencies and data as needed

if [ ! -d dependencies ]; then
    mkdir dependencies
fi

if [ ! -d data ]; then
    mkdir data
fi
if [ ! -d data/logs ]; then
    mkdir data/logs
fi


########################################################
### Dependencies/Python configuration ##################

PYCONFIG=dependencies/pyconfig.sh

if [ -e ${PYCONFIG} ]; then
    echo "Python configuration file ${PYCONFIG} exists, skipping"
    source ${PYCONFIG}
else
    # start Python configuration file
    echo '#!/bin/bash' > ${PYCONFIG}

    # configure Python installation to use
    echo "Python environment to execute with (should include tensorflow)"
    read -p "Path to binary [default: python3]: " PY
    if [ -z "${PY}" ]; then
        PY=python3
    fi
    echo "export PY=${PY}" >> ${PYCONFIG}

    echo "Checking for dependencies..."

    # check for pyemblib
    ${PY} -c "import pyemblib" 2>>/dev/null
    if [[ $? = 1 ]]; then
        echo
        echo "Cloning pyemblib..."
        cd dependencies
        git clone https://github.com/drgriffis/pyemblib.git
        cd ../
        echo "export PYTHONPATH=\${PYTHONPATH}:$(pwd)/dependencies/pyemblib" >> ${PYCONFIG}
    fi

    # check for configlogger
    ${PY} -c "import configlogger" 2>>/dev/null
    if [[ $? = 1 ]]; then
        echo
        echo "Cloning configlogger"
        cd dependencies
        git clone https://github.com/drgriffis/configlogger.git
        cd ../
        echo "export PYTHONPATH=\${PYTHONPATH}:$(pwd)/dependencies/pyemblib" >> ${PYCONFIG}
    fi

    # check for drgriffis.common
    ${PY} -c "import drgriffis.common" 2>>/dev/null
    if [[ $? = 1 ]]; then
        echo
        echo "Cloning miscutils (drgriffis.common)"
        cd dependencies
        git clone https://github.com/drgriffis/miscutils.git
        cd ../
        echo "export PYTHONPATH=\${PYTHONPATH}:$(pwd)/dependencies/miscutils/py" >> ${PYCONFIG}
    fi

    echo
    echo "Python configuration complete."
    echo "Configuration written to ${PYCONFIG}"
fi

echo
echo "Checking for analogy data..."

########################################################
### Dependencies/Python configuration ##################


function useds {
    useit=
    got_valid_yn=0
    while [[ ${got_valid_yn} = 0 ]]; do
        read -p "Use $1 dataset? [yes/no] (yes) " useit
        if [ "${useit}" = "yes" ]; then
            got_valid_yn=1
        else 
            if [ "${useit}" = "no" ]; then
                got_valid_yn=1
            fi
        fi
    done
    echo "$useit"
}

usebats=$(useds BATS)
if [ "${usebats}" == "yes" ]; then
    if [ ! -d data/BATS_3.0 ]; then
        echo
        echo "To obtain the BATS 3.0 dataset, please visit"
        echo "  http://vecto.space/projects/BATS/"
        echo "and click the 'Dataset' link."
        echo
        echo "Please place the BATS_3.0.zip file in data/"
        read -p "and press [Enter] "

        if [ -e data/BATS_3.0.zip ]; then
            echo "Unzipping BATS_3.0.zip"
            cd data
            unzip BATS_3.0.zip 1>>/dev/null
            cd ../

            echo "Creating single BATS analogy set"
            outf=data/BATS_3.0/BATS_full.txt
            ${PY} -m util.generate_single_BATS_file \
                data/BATS_3.0 \
                ${outf}
            echo "Dataset writtent to ${outf}."
            echo
        else
            echo "BATS_3.0.zip not found, skipping."
            echo "If you would like to use this dataset in future, please run $0 again."
            echo
        fi
    else
        echo "BATS dataset already set up, skipping."
    fi
fi

usebmass=$(useds BMASS)
if [ "${usebmass}" == "yes" ]; then
    if [ ! -d data/BMASS ]; then
        echo
        echo "To obtain the BMASS dataset, please visit"
        echo "  https://slate.cse.ohio-state.edu/BMASS/"
        echo "and click the 'Download' link."
        echo
        echo "Please place the BMASS.zip file in data/"
        read -p "and press [Enter] "

        if [ -e data/BMASS.zip ]; then
            echo "Unzipping BMASS.zip"
            cd data
            unzip BMASS.zip 1>>/dev/null
            cd ../
            echo "Dataset set up in data/BMASS."
            echo
        else
            echo "BMASS.zip not found, skipping."
            echo "If you would like to use this dataset in future, please run $0 again."
            echo
        fi
    else
        echo "BMASS dataset already set up, skipping."
    fi
fi
