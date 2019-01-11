# Roadmap

Here you can see what we define as critical functions we want to add in the newer versions

## Next version

* **tags**: add the ability to pass tags to the cli command. The tags define which executors will run. Look into the functionality to pass tags with `and` and `or` functionality while still being clear to the user
* **extra variables**: add the option to pass extra vars via de cli. These variables will be added to the registry automatically
* **questionables**: Add the option to ask a question before a certain executor or sequence. Also add the option to the questionables to be able to skip them if the same registry variable already exists.

## Future

These are functions that will eventually be implemented by crit but are too much into the future for now. 

Right now the idea is to add these services and make them fully open source but also add a SaaS option for those who need it

* **Secret management**: Gradually hashicorp's vault is becoming the standard for secret management. The thinking behind Vault aligns with that of crit. This is why we want to implement secret management with vault.
* **Events**: Add the ability to run a sequence when something happens on the server. This will require a 'build' server that can catch these events. The reason this is not in the base of crit is because we want to keep it simple but with the ability to upgrade
* **Create infrastructure**: Create infrastructure with crit and automatically calls a certain sequence(s) when the infrastructure is created. This also includes state management. Preferably with two options: version controllable and cloud based. This functionality will be refered to as `crit-infra`
* **UI for crit**: A UI in which you can call the `crit` and `crit-infra`
* **Autorun crit functions based on stats**: This functionality enables you to autorun `crit` or `crit-infra` based in stats of for example a sever. An example is that you can create or delete containers on demand. If the server reaches a certain cpu usage another container will be deployed and if the cpu lowers again this container will be deleted again. This is just a small example of this feature.