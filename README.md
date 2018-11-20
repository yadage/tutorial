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


## Building Docker Images

One of the main tasks

```bash
git 
docker build -t yadage/tutorial/messagewriter .
```


## Writing Individual Job Templates

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