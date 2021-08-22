var fs = require('fs');
var Web3 = require('web3');

var secrets = JSON.parse(fs.readFileSync('./secrets.json', 'utf8'));

var web3 = new Web3(new Web3.providers.HttpProvider(
    secrets.provider
));

var contract = '0x98CD3B326E1248061d684Ae230F580b74195dD86';

web3.eth.getBalance(address, (e, x) => {
    console.log(web3.utils.fromWei(x));
});
