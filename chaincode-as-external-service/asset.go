package main

type SimpleAsset struct {
	TxID    			string `json:"txID"`
	UID 				string `json:"uid"`
	UID_DESTINATION		string `json:"uid_destination"`
	TransactionID 		string `json:"transaction_id"`
	TransactionType 	string `json:"transaction_type"`
	TransactionAmount 	string `json:"transaction_amount"`
	TransactionDateTime string `json:"transaction_date_time"`
}