# generated by eelbrain/scripts/make_example_tests.py
import logging
import os
import re
import shutil
from tempfile import mkdtemp

from eelbrain import plot

dir_ = os.path.dirname(__file__)
examples_dir = os.path.join(dir_, '..', '..', 'examples')
examples_dir = os.path.abspath(examples_dir)


def test_0():
    "Test examples/datasets/align.py"
    exa_dir = os.path.join(examples_dir, 'datasets')
    exa_file = os.path.join(exa_dir, 'align.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'align.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('align.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_1():
    "Test examples/experiment/word_experiment.py"
    exa_dir = os.path.join(examples_dir, 'experiment')
    exa_file = os.path.join(exa_dir, 'word_experiment.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'word_experiment.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('word_experiment.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_2():
    "Test examples/fmtxt/report.py"
    exa_dir = os.path.join(examples_dir, 'fmtxt')
    exa_file = os.path.join(exa_dir, 'report.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'report.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('report.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_3():
    "Test examples/fmtxt/table.py"
    exa_dir = os.path.join(examples_dir, 'fmtxt')
    exa_file = os.path.join(exa_dir, 'table.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'table.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('table.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_4():
    "Test examples/meg/mne_sample_loader.py"
    exa_dir = os.path.join(examples_dir, 'meg')
    exa_file = os.path.join(exa_dir, 'mne_sample_loader.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'mne_sample_loader.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('mne_sample_loader.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_5():
    "Test examples/meg/simple meg.py"
    exa_dir = os.path.join(examples_dir, 'meg')
    exa_file = os.path.join(exa_dir, 'simple meg.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'simple meg.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('simple meg.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_6():
    "Test examples/meg/source permutation cluster.py"
    exa_dir = os.path.join(examples_dir, 'meg')
    exa_file = os.path.join(exa_dir, 'source permutation cluster.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'source permutation cluster.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('source permutation cluster.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_7():
    "Test examples/meg/source permutation.py"
    exa_dir = os.path.join(examples_dir, 'meg')
    exa_file = os.path.join(exa_dir, 'source permutation.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'source permutation.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('source permutation.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_8():
    "Test examples/meg/topographic plotting.py"
    exa_dir = os.path.join(examples_dir, 'meg')
    exa_file = os.path.join(exa_dir, 'topographic plotting.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'topographic plotting.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('topographic plotting.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_9():
    "Test examples/statistics/ANCOVA_Crawley.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'ANCOVA_Crawley.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'ANCOVA_Crawley.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('ANCOVA_Crawley.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_10():
    "Test examples/statistics/ANCOVA_rutherford.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'ANCOVA_rutherford.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'ANCOVA_rutherford.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('ANCOVA_rutherford.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_11():
    "Test examples/statistics/ANOVA.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'ANOVA.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'ANOVA.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('ANOVA.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_12():
    "Test examples/statistics/ANOVA_rutherford_1.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'ANOVA_rutherford_1.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'ANOVA_rutherford_1.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('ANOVA_rutherford_1.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_13():
    "Test examples/statistics/ANOVA_rutherford_2.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'ANOVA_rutherford_2.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'ANOVA_rutherford_2.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('ANOVA_rutherford_2.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_14():
    "Test examples/statistics/Fox_Prestige.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'Fox_Prestige.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'Fox_Prestige.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('Fox_Prestige.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_15():
    "Test examples/statistics/pdf.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'pdf.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'pdf.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('pdf.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)

def test_16():
    "Test examples/statistics/simple.py"
    exa_dir = os.path.join(examples_dir, 'statistics')
    exa_file = os.path.join(exa_dir, 'simple.py')

    # find required files
    with open(exa_file) as fid:
        text = fid.read()
    filenames = re.findall("# requires: (\w+.\w+)", text)
    text = text.replace("n_samples = 1000", "n_samples = 2")

    # copy all files to temporary dir
    tempdir = mkdtemp()
    dst = os.path.join(tempdir, 'simple.py')
    with open(dst, 'w') as fid:
        fid.write(text)
    for filename in filenames:
        src = os.path.join(exa_dir, filename)
        shutil.copy(src, tempdir)

    # execute example
    logging.info("executing from %s" % tempdir)
    plot.configure(show=False)
    os.chdir(tempdir)
    execfile('simple.py', {})

    # delete temporary files
    shutil.rmtree(tempdir)
