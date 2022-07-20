package main

import (
	"crypto/sha256"
	"errors"
	"fmt"
	"math"
	"math/rand"
	"time"
)

type Problem []int
type Assignment []int
type Witness []int

func main() {

	rand.Seed(time.Now().UnixNano())

	problem := Problem{4, 11, 8, 1}
	assignment := Assignment{1, -1, 1, -1}

	witness, err := getWitness(problem, assignment)
	if err != nil {
		panic(err)
	}
	fmt.Println(witness)
}

func getWitness(problem Problem, assignment Assignment) (witness Witness, err error) {
	sum := 0
	maxValue := 0
	sideObfuscator := 1 - 2*rand.Intn(2)
	witness = append(witness, sum)

	if len(problem) != len(assignment) {
		err = errors.New("problem is not fitable with assignment")
		return
	}

	for i, value := range problem {
		side := assignment[i]
		if side != 1 && side != -1 {
			err = errors.New("assignment have invalide number")
			return
		}

		sum += side * value * sideObfuscator
		witness = append(witness, sum)
		if value > maxValue {
			maxValue = value
		}
	}

	if sum != 0 {
		return
	}
	shift := rand.Intn(maxValue)

	vsm := make([]int, len(witness))
	for i, v := range witness {
		vsm[i] = v + shift
	}
	return vsm, nil
}

func hashString(str string) string {
	h := sha256.New()
	h.Write([]byte(str))
	return string(h.Sum(nil))
}

type MerkleTree struct {
	data []int
	tree []string
}

func NewMerkleTree(data []int) MerkleTree {

	nextPowOf2 := int(math.Pow(2, math.Ceil(math.Log2(float64(len(data))))))
	appendedArray := make([]int, nextPowOf2-len(data), 0)
	appendedData := append(data, appendedArray...)
	tree := make([]string, 0)
	for range appendedData {
		tree = append(tree, "")
	}
	for _, data := range appendedData {
		tree = append(tree, hashString(fmt.Sprint(data)))
	}

	for i := range appendedData {
		i = len(appendedData) - 1 - i
		tree[i] = hashString(tree[i*2] + tree[i*2+1])

	}

	return MerkleTree{
		data: data,
		tree: tree,
	}
}

func (trie MerkleTree) Root() string {
	return trie.tree[1]
}
