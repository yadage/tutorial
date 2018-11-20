# tutorial

## Installing

If you are on your laptop you can install yadage via

```
pip install yadage
```

If you'd like to visualize workflows add `[viz]` to the command
in order to install the necessary dependencies

```
pip install yadage[viz]
```

### Using on LXPLUS at CERN (for high energy physicists)

Usually you cannot easily install custom python packages on LXPLUS, 
therefore a pre-setup version is installed and usable from the 
`lxplus-cloud` flavor of nodes

```
ssh lxplus-cloud.cern.ch
source ~recast/public/setup.sh
```


## Where is this going?

In this tutorial we will build a simple workflow that runs two tasks one 
after the other.

1. The first task runs a program that takes in a message string and writes
   it out to an output file
   
   The program that does this is written in C++


2. The second tasks reads in the file written by the first task and transforms
   its contents into all upper case letters

   The program for this step is writte in Python.


## Building Docker Images

One of the main ideas of yadage is to orchestrate workflows where each step
in the workflow runs in its own sandbox. This efficiently separates the domain-
specific code in the sandbox from the workflow logic.

As a sandboxing technology Linux Containers that you can e.g. build with `docker` are 
very popular. For this tutorial we are building two container images, one for
the C++ program and one for the Python program.

The images are already built and available at 

https://hub.docker.com/r/yadage/tutorial-messagewriter/

and 

https://hub.docker.com/r/yadage/tutorial-uppermaker/

if you want to build them yourself you can do

```bash
cd images/message_writer
docker build -t <username>/tutorial-messagewriter .
docker push <username>/tutorial-messagewriter
```

or

```
cd images/message_writer
docker build -t <username>/tutorial-uppermaker .
docker push <username>/tutorial-uppermaker
```

where `<username>` is your Docker Hub username. This will assemble the
Docker images on your laptop (`docker build`). In the case of the C++
program it will compile the program while for the Python program it will
simply copy the program into the container image.

The images then contain all dependencies. That is, not only the programs
themselves but also the operating system and programming language runtime
(C++ and Python respectively) needed to *execute* the programs as well.

### Testing the images

As the images include all dependencies we can now 'pull' the Docker image
on any other computer and run the programs

```
docker run --rm -it yadage/tutorial-messagewriter sh
/code # /code/message_writer hello outputfile.txt
Hello World. We will write this message: hello
Done! try looking into outputfile.txt
/code # cat outputfile.txt 
Hello, the message was: hello
/code # exit
```

Note, how after you exit all traces of the container and the output file you just created
are gone. The advantage of Linux Container technology is *isolation* and containers
that you run using `docker run` are *ephemeral*.

Each new container that you run using `docker run` starts off in exactly the same state, 
which is great for reproducibility. 

We can also test the second container image

```
/ # echo shout this > input.txt
/ # python /code/uppermaker.py input.txt output.txt
INFO:uppermaker:Hello There, we will take the contents of input.txt
INFO:uppermaker:and make them all UPPER CASE!!
INFO:uppermaker:Find the result in output.txt
/ # cat output.txt 
SHOUT THIS
/ # exit
```

#### Sharing State

While the ephemeral nature of containers is nice, sometimes you do want to persist some
data that you created within the container, perhaps because you want to do something else
with this. For this we can *loosen* the strict isolation of the container a bit and
'mount* a directory from the host computer into the container

```
docker run --rm -it -v $PWD/savehere:/data yadage/tutorial-messagewriter sh
/code # /code/message_writer hello /data/outputfile.txt
/code # cat /data/outputfile.txt 
Hello, the message was: hello
/code # exit
```

`-v  $PWD/savehere:/data` instructs docker to map the `$PWD/savehere` directory on your
host computer into the `/data` directory within the container. So files that you write 
into `/data` within the container get persisted.

We can now see the output file in `savehere/outputfile.txt`
``` 
cat savehere/outputfile.txt
Hello, the message was: hello
```

```
docker run --rm -it -v $PWD/savehere:/data yadage/tutorial-uppermaker sh
/ # python /code/uppermaker.py /data/outputfile.txt /data/secondfile.txt
/ # exit
cat savehere/secondfile.txt 
HELLO, THE MESSAGE WAS: HELLO
```

This seems great! we can use pre-packaged software archived in docker images to run the series of commands
that we want. But we had to manage a lot of things by hand: e.g. running Docker with the right flags to 
persist the data and executing the commands in the right order. I.e. we needed to exactly know *how* to do 
these things, which is sometimes referred to as a "imperative style" or computing.

In the following we will now introduce a more "declarative" style in which we only specify *what* we want
to do and let a "workflow engine", i.e. `yadage`, figure out *how* to do it.

## Writing Individual Job Templates

In order to make re-usable workflows we need to not only know concrete commands
but rather "command templates" such that we can use these templates to create
*new commands* once we e.g. have the correct inputs available.


```yaml
messagewriter:
  process:
    process_type: interpolated-script-cmd
    script: |
      /code/message_writer '{message}' {outputfile}
  publisher:
    publisher_type: interpolated-pub
    publish:
      msgfile: '{outputfile}'
  environment:
    environment_type: docker-encapsulated
    image: yadage/tutorial-messagewriter
```

```
packtivity-validate steps.yml#/messagewriter
```

```
packtivity definition is valid
```

```
packtivity-run steps.yml#/messagewriter -p message="Hi there." -p outputfile="'{workdir}/outputfile.txt'" --write first
    ```


```
cat first/outputfile.txt 

```
Hello, the message was: Hi there.
```



```
messagewriter:
  process:
    process_type: interpolated-script-cmd
    script: |
      /code/message_writer '{message}' {outputfile}
  publisher:
    publisher_type: interpolated-pub
    publish:
      msgfile: '{outputfile}'
  environment:
    environment_type: docker-encapsulated
    image: yadage/tutorial-messagewriter

upppermaker:
  process:
    process_type: interpolated-script-cmd
    script: |
      /code/uppermaker.py {inputfile} {outputfile}
  publisher:
    publisher_type: interpolated-pub
    publish:
      shoutingfile: '{outputfile}'
  environment:
    environment_type: docker-encapsulated
    image: yadage/tutorial-uppermaker
```


```
packtivity-run steps.yml#/upppermaker -p inputfile="$PWD/first/outputfile.txt" -p outputfile="'{workdir}/outputfile.txt'" --write second --read first
```

```
cat second/outputfile.txt
```

```
HELLO, THE MESSAGE WAS: HI THERE.
```

## Writing the Workflow

```yaml
stages:
- name: writing_stage
  dependencies: [init]
  scheduler:
    scheduler_type: singlestep-stage
    parameters:
      message: {step: init, output: msg}
      outputfile: '{workdir}/outputfile.txt'
    step: {$ref: 'steps.yml#/messagewriter'}
- name: shouting_stage
  dependencies: [writing_stage]
  scheduler:
    scheduler_type: singlestep-stage
    parameters:
      inputfile: {step: writing_stage, output: msgfile}
      outputfile: '{workdir}/outputfile.txt'
    step: {$ref: 'steps.yml#/upppermaker'}
```


```
yadage-run workdir workflow.yml -p msg='Hi there.' --visualize
```

```
cat workdir/writing_stage/outputfile.txt
```

```
Hello, the message was: Hi there.
```

```
cat workdir/shouting_stage/outputfile.txt
```

```
HELLO, THE MESSAGE WAS: HI THERE.
```