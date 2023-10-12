kubectl exec -it -n dummy-com $(kubectl get pod -n dummy-com -l component=cli.peer0.org1.dummy.com -o jsonpath={.items[0].metadata.name}) -- bash -c "peer chaincode invoke -o orderer0-dummy-com:7050 --tls --cafile /etc/hyperledger/fabric/crypto/ordererOrganizations/dummy.com/orderers/orderer0.dummy.com/msp/tlscacerts/tlsca.dummy.com-cert.pem -C channelall -n chaincode-as-external-service  --peerAddresses peer0-org1-dummy-com:7051 --tlsRootCertFiles /etc/hyperledger/fabric/crypto/peerOrganizations/org1.dummy.com/peers/peer0.org1.dummy.com/tls/ca.crt  --peerAddresses peer0-org2-dummy-com:7051 --tlsRootCertFiles /etc/hyperledger/fabric/crypto/peerOrganizations/org2.dummy.com/peers/peer0.org2.dummy.com/tls/ca.crt -c '{\"Args\":[\"Store\", \"1234\", \{asdad:1234}\"]}'"