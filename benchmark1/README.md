#benchmark organization
    code
        directory for the benchmark code autoencoder auen4.1.ff.py
    data
        directory for input data (training and testing files)
    doc
        directory for documentation about the benchmark
    jobs
        (placeholder) directory for platform-specific job scripts
        test.sh: sample invocation script
    plots
        (placeholder) directory to put graphs (if any) generated from the benchmark
    results
        directory to put the json results file generated from the benchmark

#install requirements (if needed)
pip install -r requirements.txt

#usage help
python code/auen4.1.ff.py --help

    usage: auen4.1.ff.py [-h] [-t TARGET] [-m METHOD] [-b BACKEND] [-v VENDOR]
                         [--version] --user USER --trainfile TRAINFILENAME
                         --testfile TESTFILENAME --outputfile OUTPUTFILENAME

    optional arguments:
      -h, --help            show this help message and exit
      -t TARGET             target hardware
      -m METHOD             method
      -b BACKEND            backend; tf: tensorflow, th:theano
      -v VENDOR             vendor
      --version             show program's version number and exit

    required arguments:
      --user USER           user name
      --trainfile TRAINFILENAME
                            train file name
      --testfile TESTFILENAME
                            test file name
      --outputfile OUTPUTFILENAME
                            output file name

#run

python ../code/auen4.1.ff.py --user pbalapra --trainfile ../data/breast.train1.csv --testfile ../data/breast.test1.csv --outputfile ../results/result.json

#check the output

$cat result.json
[
	{   "unixTimeStamp": 1480392401.783029,
        "metricValue": 0.029148954898118973,
        "target": null,
        "benchmarkName": "benchmark1",
        "trainTime": 29.71419405937195,
        "initTime": 0.0344080924987793,
        "metric": "mse",
        "outputFileName": "../results/result.json",
        "testTime": 2.0379559993743896,
        "trainFileName": "../data/breast.train1.csv",
        "user": "pbalapra",
        "epocs": 2,
        "installedPackages": ["cycler==0.10.0", "funcsigs==1.0.2", "h5py==2.6.0", "keras==1.1.1", "matplotlib==1.5.3", "mock==2.0.0", "numexpr==2.6.1", "numpy==1.11.2", "pandas==0.19.1", "pbr==1.10.0", "pip==9.0.1", "progressbar==2.3", "protobuf==3.0.0b2", "pyparsing==2.1.10", "python-dateutil==2.6.0", "pytz==2016.7", "pyyaml==3.12", "scikit-learn==0.18", "scipy==0.18.1", "setuptools==28.8.0", "six==1.10.0", "tables==3.3.0", "tensorflow==0.10.0", "theano==0.8.2", "wheel==0.29.0"],
        "vendor": null,
        "testFileName": "../data/breast.test1.csv",
        "type": "autoencoder",
        "method": "dl",
        "backend": "tf"
    }
]

#import the results to the leaderboard database
python leaderboard.py --benchmarkName benchmark1 --jsonFileName ../results/result.json

# query the leaderboard database for benchmark1
python leaderboard.py --benchmarkName benchmark1

# putting everything together in a single script
cd jobs; sh test.sh
