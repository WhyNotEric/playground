package main

import "fmt"

func main() {
	// Test
	r := gcd(18, 12)
	fmt.Printf("18 and 12 have gcd is %d \n", r)

	r, x, y := ext_gcd(252, 198)
	fmt.Printf("252 and 198 have gcd is %d \n", r)
	fmt.Printf("252 and 198 x y is %d, %d \n", x, y)

	r, x, y = ext_gcd_without_recursive(252, 198)
	fmt.Printf("252 and 198 have gcd is %d \n", r)
	fmt.Printf("252 and 198 x y is %d, %d \n", x, y)
}

func gcd(a int64, b int64) int64 {
	a = Max(a, b)
	b = Min(a, b)

	if b == 0 {
		return a
	}
	return gcd(b, a%b)
}

func ext_gcd(a int64, b int64) (r int64, x int64, y int64) {
	if b == 0 {
		x = 1
		y = 0
		r = a
		return
	}

	r, x1, y1 := ext_gcd(b, a%b)
	x = y1
	y = x1 - a/b*y1
	return
}

func ext_gcd_without_recursive(a int64, b int64) (r int64, x int64, y int64) {
	var t0 int64 = 1
	var t1 int64 = 0
	var s0 int64 = 0
	var s1 int64 = 1

	r = a % b
	q := a / b

	for r != 0 {
		x = t0 - q*t1
		y = s0 - q*s1

		t0 = t1
		s0 = s1
		t1 = x
		s1 = y

		a = b
		b = r
		r = a % b
		q = a / b

	}
	r = b
	return
}

// Max returns the larger of x or y.
func Max(x, y int64) int64 {
	if x < y {
		return y
	}
	return x
}

// Min returns the smaller of x or y.
func Min(x, y int64) int64 {
	if x > y {
		return y
	}
	return x
}

func inverse(a int64, n int64) (r int64, x int64) {
	var t0 int64 = 0
	var t1 int64 = 1
	var r0 int64 = n
	var r1 int64 = a

	for r1 != 0 {
		q := r0 / r1

		t0, t1 = t1, t0-q*t1
		r0, r1 = r1, r0-q*r1
	}

	if r > 1 {
		fmt.Printf("a is not invertible")
		return
	}

	if t0 < 0 {
		t0 = t0 + n
	}
	x = t0
	return
}
