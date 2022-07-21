package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"math"
	"math/rand"
	"strconv"
	"strings"
)

type Problem []int
type Assignment []int
type Witness []int

var Random = 1

func main() {

	// rand.Seed(time.Now().UnixNano())

	// problem := Problem{4, 11, 8, 1}
	// assignment := Assignment{1, -1, 1, -1}

	// witness, err := getWitness(problem, assignment)
	// if err != nil {
	// 	panic(err)
	// }
	// fmt.Println(witness)

	zkp := test(10)
	fmt.Printf("Make a zkp work? %t", zkp)
}

func test(q int) bool {
	problem := []int{1, 2, 3, 6, 6, 6, 12}
	assignment := []int{1, 1, -1, -1, -1, -1, 1}
	proof, err := getProof(problem, assignment, q)
	if err != nil {
		fmt.Println(err)
		return false
	}
	fmt.Print("\n")
	fmt.Println(proof)
	return verifyProof(problem, proof)
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
	fmt.Printf("\n getWintness:")
	fmt.Println(vsm)
	return vsm, nil
}

func hashString(str string) string {
	h := sha256.New()
	h.Write([]byte(str))
	return hex.EncodeToString(h.Sum(nil))
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

	for _, d := range appendedData {
		tree = append(tree, hashString(fmt.Sprint(d)))
	}

	for i := range appendedData {
		i = len(appendedData) - 1 - i
		tree[i] = hashString(tree[i*2] + tree[i*2+1])
	}

	fmt.Print("\n NewMerkleTree: ")
	fmt.Print(data)
	fmt.Print(appendedData)
	fmt.Print(tree)
	return MerkleTree{
		data: data,
		tree: tree,
	}
}

func (trie MerkleTree) Root() string {
	return trie.tree[1]
}

func (trie MerkleTree) GetValueAndPath(idx int) (int, []string) {
	val := trie.data[idx]
	authPath := make([]string, 0)
	idx = idx + len(trie.data)
	for idx > 1 {
		authPath = append(authPath, trie.tree[idx^1])
		idx = idx / 2
	}
	return val, authPath
}

func verifyMerklePath(root string, dataSize int, valueId int, value string, path []string) (bool, error) {
	curr := hashString(value)
	treeNodeId := valueId + int(math.Pow(2, math.Ceil(math.Log2(float64(dataSize)))))
	for _, sibling := range path {
		if treeNodeId < 1 {
			return false, errors.New("tree node id < 1")
		}
		if treeNodeId%2 == 0 {
			curr = hashString(curr + sibling)
		} else {
			curr = hashString(sibling + curr)
		}
		treeNodeId = treeNodeId / 2
	}
	if treeNodeId != 1 {
		return false, errors.New("internal error")
	}
	return root == curr, nil
}

func getProof(problem Problem, assignment Assignment, num_queries int) (proof [][]string, err error) {

	randomnessSeed := 0
	for _, p := range problem {
		randomnessSeed += p
	}

	for range make([]int, num_queries) {
		witness, err := getWitness(problem, assignment)
		if err != nil {
			break
		}
		tree := NewMerkleTree(witness)
		rand.Seed(int64(randomnessSeed))
		queryIdx := rand.Intn(len(problem) + 1)
		queryAndResp := []string{tree.Root()}
		queryAndResp = append(queryAndResp, fmt.Sprint(queryIdx))
		val, path := tree.GetValueAndPath(queryIdx)
		queryAndResp = append(queryAndResp, fmt.Sprint(val), strings.Join(path[:], ","))
		val2, path2 := tree.GetValueAndPath((queryIdx + 1) % len(witness))
		queryAndResp = append(queryAndResp, fmt.Sprint(val2), strings.Join(path2[:], ","))
		proof = append(proof, queryAndResp)
		randomnessSeed += Random // magic number, must same as 186 line
	}
	return proof, nil
}

func boolBitwiseAnd(pre bool, aft bool) bool {
	if pre == aft && pre {
		return true
	} else {
		return false
	}
}

func verifyProof(problem Problem, proof [][]string) bool {
	proofChecksOut := true
	randomnessSeed := 0
	for _, p := range problem {
		randomnessSeed += p
	}

	for _, query := range proof {
		rand.Seed(int64(randomnessSeed))
		queryIdx := rand.Intn(len(problem) + 1)
		fmt.Printf("\n validate proof with query idx: %d", queryIdx)
		merkleRoot := query[0]
		proofChecksOut = boolBitwiseAnd(proofChecksOut, fmt.Sprint(queryIdx) == query[1])

		if queryIdx < len(problem) {
			val, _ := strconv.Atoi(query[2])
			two := float64(val)
			fmt.Printf("\n val2: %f", two)
			val, _ = strconv.Atoi(query[4])
			four := float64(val)
			fmt.Printf("\n val4: %f", four)
			proofChecksOut = boolBitwiseAnd(proofChecksOut, math.Abs(two-four) == math.Abs(float64(problem[queryIdx])))
		} else {
			fmt.Print("validate the last value")
			fmt.Printf("\n val2: %s", query[2])
			fmt.Printf("\n val4: %s", query[4])
			proofChecksOut = query[2] == query[4]
		}

		out, _ := verifyMerklePath(merkleRoot, len(problem)+1, queryIdx, query[2], strings.Split(query[3], ","))
		proofChecksOut = boolBitwiseAnd(proofChecksOut, out)

		out, _ = verifyMerklePath(merkleRoot, len(problem)+1, (queryIdx+1)%(len(problem)+1), query[4], strings.Split(query[5], ","))
		proofChecksOut = boolBitwiseAnd(proofChecksOut, out)
		randomnessSeed += Random // magic number, must same as 160 line
	}
	return proofChecksOut
}
