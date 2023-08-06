# aws-opsworks-smooth-deploy
Deploy script executed inside AWS opsworks instances to avoid error request from ELB.


Before starting the deployment process, execute

```
aws-opsworks-smooth-deploy detach --opsworks-stack-id=<STACK-ID>
```

After the deployment process finish, execute

```
aws-opsworks-smooth-deploy attach --opsworks-stack-id=<STACK-ID>
```
