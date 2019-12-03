class Point {
    constructor (P, curve) {
        this.x = P[0];
        this.y = P[1];
        this.curve = curve;
    }

    equal(Q) {
        return this.x == Q.x && this.y == Q.y;
    }

    add(Q) {
        if (this.equal(Q)) {
            return this.dbl();
        }

        var cp = this.curve.p;

        var l_mod = bigInt(Q.x - this.x).modPow(cp - 2n, cp).value;
        var l = (Q.y - this.y) * l_mod;

        var xr_mod = l*l - this.x - Q.x;
        var xr = ((xr_mod % cp) + cp) % cp;

        var yr_mod = l*(this.x - xr) - this.y;
        var yr = ((yr_mod % cp) + cp) % cp;

        return new Point([xr, yr], this.curve)
    }

    dbl() {
        var cp = this.curve.p;

        var l_mod = 2n * this.y;
        var l = (3n*this.x*this.x + this.curve.a) * (bigInt(l_mod).modPow(cp - 2n, cp)).value;

        var xr_mod = l*l - this.x - this.x;
        var xr = ((xr_mod % cp) + cp) % cp;

        var yr_mod = l*(this.x - xr) - this.y;
        var yr = ((yr_mod % cp) + cp) % cp;

        return new Point([xr, yr], this.curve)
    }

    dbladd(k) {
        if (k == 0n) {
            return new Point([0, 0], this.curve);
        }
        else if (k == 1n) {
            return new Point([this.x, this.y], this.curve);
        }
        else if (k % 2n == 1n) {
            return this.add(this.dbladd(k - 1n));
        }
        else {
            return this.dbl().dbladd(k / 2n);
        }
    }
}


class Curve {
    constructor(p, a, b, G) {
        this.p = p;
        this.a = a;
        this.b = b;
        this.G = G;
    }
}


var alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

secp256k1 = new Curve(
    bigInt('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F', 16).value,
    0n,
    7n,
    [
        bigInt('79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798', 16).value,
        bigInt('483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8', 16).value,
    ],
);

function genPub(k) {
    var gp = new Point(secp256k1.G, secp256k1);
    var q = gp.dbladd(k)
    return bigInt(q.x).toString(58, alphabet) + "/" + bigInt(q.y).toString(58, alphabet);
}

function ecdh(x, y, k) {
    var pub = new Point([x, y], secp256k1);
    var secret = pub.dbladd(k);
    return bigInt(secret.x).toString(16);
}
