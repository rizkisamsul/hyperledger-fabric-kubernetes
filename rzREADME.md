
## Usage

- Assuming you have minikube running:

```bash
./deploy.sh
# wait until all resources are up and running
watch -n 1 kubectl get -n dummy-com pods,ingress,secrets,svc,pvc,pv
```

Now, we are going to operate the peer of Org1 and the peer of Org2 in order to create and join a channel as well as install the chaincode.

You'll need two different terminals and run the following commands:

- Terminal 1: CLI configured for the peer of Org1

```bash
# connect to the pod running the CLI for peer0.org1
kubectl exec -it -n dummy-com $(kubectl get pod -n dummy-com -l component=cli.peer0.org1.dummy.com -o jsonpath="{.items[0].metadata.name}") -- bash
cd artifacts
peer channel create -c $CHANNEL_NAME -f ./channelall.tx -o orderer0-dummy-com:7050 --tls --cafile $ORDERER_CA
peer channel join -b ./channelall.block
cd -
```

- Terminal 2: CLI configured for the peer of Org2

```bash
# connect to the pod running the CLI for peer0.org2
kubectl exec -it -n dummy-com $(kubectl get pod -n dummy-com -l component=cli.peer0.org2.dummy.com -o jsonpath="{.items[0].metadata.name}") -- bash

cd artifacts
peer channel join -b ./channelall.block
cd -
```

At this point the channel has been created, and both peers of Org1 and Org2 have joined the channel.

We can now proceed to install the chaincode.

- Terminal 1: CLI configured for the peer of Org1

tar -cvzf backup.tgz /home/user/project

```bash
# install the chaincode
peer lifecycle chaincode install ./chaincodes/chaincode-as-external-service/chaincode-as-external-service.tgz
peer lifecycle chaincode approveformyorg  -o orderer0-dummy-com:7050 --tls --cafile $ORDERER_CA --channelID $CHANNEL_NAME --name chaincode-as-external-service --version 1.0 --init-required --package-id chaincode-as-external-service:33b295bb4ac3f8dead7bddb9e86315aa7b3729b76d6d53f9379ddba6db900f7f --sequence 1
```

- Terminal 2: CLI configured for the peer of Org2

```bash
# install the chaincode
peer lifecycle chaincode install ./chaincodes/chaincode-as-external-service/chaincode-as-external-service.tgz
peer lifecycle chaincode approveformyorg  -o orderer0-dummy-com:7050 --tls --cafile $ORDERER_CA --channelID $CHANNEL_NAME --name chaincode-as-external-service --version 1.0 --init-required --package-id chaincode-as-external-service:33b295bb4ac3f8dead7bddb9e86315aa7b3729b76d6d53f9379ddba6db900f7f --sequence 1
```

We are almost done, chaincode has been approved by both Org1 and Org2, we can now commit the chaincode before invoking it.

- Terminal 1: CLI configured for the peer of Org1

```bash
# You can check the commit readiness of the chaincode by running:
peer lifecycle chaincode checkcommitreadiness -o orderer0-dummy-com:7050 --channelID $CHANNEL_NAME --tls --cafile $ORDERER_CA --name chaincode-as-external-service --version 1.0 --init-required --sequence 1

# It should output something like:
# Chaincode definition for chaincode 'chaincode-as-external-service', version '1.0', sequence '1' on channel 'channelall' approval status by org:
# Org1MSP: true
# Org2MSP: true
# Org3MSP: false


# commit the chaincode
peer lifecycle chaincode commit -o orderer0-dummy-com:7050 --channelID $CHANNEL_NAME --name chaincode-as-external-service --version 1.0 --sequence 1 --init-required --tls --cafile $ORDERER_CA --peerAddresses peer0-org1-dummy-com:7051 --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE  --peerAddresses peer0-org2-dummy-com:7051 --tlsRootCertFiles /etc/hyperledger/fabric/crypto/peerOrganizations/org2.dummy.com/peers/peer0.org2.dummy.com/tls/ca.crt
```

That's it ! The chaincode is ready to be invoked :smile:.

- Terminal 1: CLI configured for the peer of Org1

```bash
# init and invoke the chaincode
peer chaincode invoke -o orderer0-dummy-com:7050 --tls --cafile $ORDERER_CA -C $CHANNEL_NAME -n chaincode-as-external-service  --peerAddresses peer0-org1-dummy-com:7051 --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE  --peerAddresses peer0-org2-dummy-com:7051 --tlsRootCertFiles /etc/hyperledger/fabric/crypto/peerOrganizations/org2.dummy.com/peers/peer0.org2.dummy.com/tls/ca.crt --isInit -c '{"function":"Init","Args":[]}'
```

- Terminal 2: CLI configured for the peer of Org2

```bash
# query the chaincode
peer chaincode query -C $CHANNEL_NAME -n chaincode-as-external-service -c '{"Args":["Query", "default-asset"]}'
```

## Exposing Fabric components through an Ingress

Before we clean everything, let's take a look at how to expose Fabric components through a Kubernetes Ingress.
As we are running our demo against `minikube`, we need to enable the ingress addon.

NB: For macOS users, you need to install [this](https://github.com/chipmk/docker-mac-net-connect) before going further.

```bash
minikube addons enable ingress
```

Before pursuing, ensure that the Nginx Ingress Controller is running properly:

```bash
kubectl get pods -n ingress-nginx

NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-585xm        0/1     Completed   0          8m44s
ingress-nginx-admission-patch-mzsng         0/1     Completed   0          8m44s
ingress-nginx-controller-5959f988fd-nmffb   1/1     Running     0          8m44s
```

Everything is fine, we can proceed and deploy our ingress:

```bash
kubectl apply -f k8s/ingress/orderer0.yaml
```

We are almost done, as we are running our demo locally we need a few more things to setup:

```bash
# retrieve the external IP
EXTERNAL_IP=$(minikube ip)

# configure your local setup
sudo -- sh -c 'echo "\n'"$EXTERNAL_IP"' operations.orderer0.dummy.com\n" >> /etc/hosts'
```

That's it ! Let's run a health check of the `orderer0.dummy.com` :smile:.

```bash
curl https://operations.orderer0.dummy.com/healthz -Lk
{"status":"OK","time":"2022-12-02T10:35:39.704828282Z"}
```


## Cleanup

```bash
kubectl delete statefulset,deployment,ingress,service,job,secrets,pvc --all --namespace dummy-com && kubectl delete pv local-volume
```
