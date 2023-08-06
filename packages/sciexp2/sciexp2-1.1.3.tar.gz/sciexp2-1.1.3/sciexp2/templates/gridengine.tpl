#!/bin/bash
# Launch script for clusters using gridengine
#
# Job name
#$ -N @JOB_NAME@
# Specify a shell
#$ -S /bin/bash
# When to send me a mail
#$ -m @QSUB_MAIL@
#$ -M @EMAIL@
# Job standard output
#$ -o @JOB_STDOUT@
# Job standard error
#$ -e @JOB_STDERR@
# Job standard input
#$ -i @JOB_STDIN@
# User-defined options to 'qsub'
@QSUB_OPTS@


# Executes everything from the base directory (Launchgen.out, set as $BASE),
# which must be available from all execution nodes.
#
# Files for the execution and results should be copied to/from local filesystems
# in SYNCIN/SYNCOUT in order to minimize network usage (e.g., if the cluster has
# a networked filesystem and a local scratch zone).
#
# When starting, $DONE is removed and $FAIL is set to an empty file. If CMD
# executes successfully, $FAIL is removed.
#
# The script exits at the first failing command.
#
# If you kill a job and re-launch it, the old job might still generate some
# files even after the new job has started execution. In order to avoid file
# clobbering from the old job into the files of the new job, you can uniquify
# temporal directory and file names with gridengine's $JOB_ID variable or the
# mktemp command.


##################################################
# Environment preparation

# Unbuffer stdout, so that stdout/stderr appear in the correct order if they
# point to the same file
stdbuf -o0 -e0 echo -n
# Early fail
set -e
# Early abort on first error (including inside a chain of pipes)
set -o pipefail;

# Absolute paths to important directories / files
# (created by gridengine before manually cd'ing into $BASE)
JOB_STDOUT=`readlink -f @JOB_STDOUT@`
JOB_STDERR=`readlink -f @JOB_STDERR@`

# Absolute path to base directory
BASE=${LAUNCHER_BASE}
if [ -z "$BASE" ]; then
    # Not executing with launcher; detect base directory
    # (LAUNCHER cannot be outside BASE)
    BASE=`readlink -f $0`
    BASE=${BASE%@LAUNCHER@}
fi
# Start at base directory
cd $BASE

# Create output directories
mkdir -p `dirname @STDOUT@`
mkdir -p `dirname @STDERR@`
mkdir -p `dirname @DONE@`
mkdir -p `dirname @FAIL@`

# Absolute paths to important directories / files
STDOUT=`readlink -f @STDOUT@`
STDERR=`readlink -f @STDERR@`
FAIL=`readlink -f @FAIL@`
DONE=`readlink -f @DONE@`

# Start with a clean slate
# (do not remove if already exists as JOB_STDOUT/JOB_STDERR)
[ "$DONE" = "$JOB_STDOUT" -o "$DONE" = "$JOB_STDERR" ] || rm -Rf $DONE && touch $DONE
[ "$FAIL" = "$JOB_STDOUT" -o "$FAIL" = "$JOB_STDERR" ] || rm -Rf $FAIL && touch $FAIL

_redirect()
{
    if [ "$1" = "$JOB_STDOUT" -o "$1" = "$JOB_STDERR" ]; then
        tee /dev/null
    else
        tee -a "$1"
    fi
}


##################################################
# Synchronize files to be used
(
@SYNCIN@
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
) 1> >(_redirect $STDOUT) 2> >(_redirect $STDERR >&2)


##################################################
# User-specified commands
(
@CMD@
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
) 1> >(_redirect $STDOUT) 2> >(_redirect $STDERR >&2)


##################################################
# Copy results back
(
@SYNCOUT@
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
) 1> >(_redirect $STDOUT) 2> >(_redirect $STDERR >&2)


##################################################
# Error checking

# Ensure the job will be detected as done, and not as failed
touch $DONE
rm -Rf $FAIL
