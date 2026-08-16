import { randomBytes } from 'node:crypto';
import * as bip39 from 'bip39';
import * as bitcoin from 'bitcoinjs-lib';
import { BIP32Factory } from 'bip32';
import * as ecc from '@bitcoinerlab/secp256k1';
import { writeFileSync, mkdirSync } from 'node:fs';

bitcoin.initEccLib(ecc);
const BIP32 = BIP32Factory(ecc);

const entropy = randomBytes(32);
const mnemonic = bip39.entropyToMnemonic(entropy);
const seed = await bip39.mnemonicToSeed(mnemonic);
const root = BIP32.fromSeed(seed);
const account = root.derivePath("m/84'/0'/0'");
const xpub = account.neutered().toBase58();

const addrs = [];
for (let i = 0; i < 5; i++) {
  addrs.push(bitcoin.payments.p2wpkh({ pubkey: account.derive(0).derive(i).publicKey }).address);
}

console.log('MNEMONIC:', mnemonic);
console.log('XPUB (m/84h/0h/0h):', xpub);
console.log('ADDRESSES (native segwit):');
addrs.forEach((a, i) => console.log(`  m/84h/0h/0h/0/${i}: ${a}`));

mkdirSync(process.env.HOME + '/.secrets', { recursive: true });
writeFileSync(process.env.HOME + '/.secrets/bip39-mnemonic.txt', mnemonic + '\n', { mode: 0o600 });
writeFileSync(process.env.HOME + '/.secrets/bip39-seed-hex.txt', seed.toString('hex') + '\n', { mode: 0o600 });
writeFileSync('public-info.json', JSON.stringify({ network: 'bitcoin', derivation: "m/84'/0'/0'", xpub, addresses: addrs, note: 'PUBLIC receive info only. Private keys/mnemonic NEVER in repo.' }, null, 2));
console.log('saved secrets (600) + public-info.json');
