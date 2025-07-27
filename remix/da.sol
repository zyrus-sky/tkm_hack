// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StudentAgency {
    address public owner;

    struct Student {
        uint256 grade;
        uint256 hackathonWins;
        uint256 healthHB;
        uint256 karma;
    }

    mapping(address => Student) private students;

    // Events
    event GradeUpdated(address indexed student, uint256 grade);
    event HealthUpdated(address indexed student, uint256 healthHB);
    event HackathonUpdated(address indexed student, uint256 wins);
    event KarmaTransferred(address indexed from, address indexed to, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not agency");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // --- Agency-only functions ---
    function setGrade(address student, uint256 grade) public onlyOwner {
        students[student].grade = grade;
        emit GradeUpdated(student, grade);
    }

    function setHealthHB(address student, uint256 hb) public onlyOwner {
        students[student].healthHB = hb;
        emit HealthUpdated(student, hb);
    }

    function setHackathonWins(address student, uint256 wins) public onlyOwner {
        students[student].hackathonWins = wins;
        emit HackathonUpdated(student, wins);
    }

    function batchAddKarma(address[] calldata studentAddrs, uint256[] calldata karmas) external onlyOwner {
        require(studentAddrs.length == karmas.length, "Mismatched input");
        for (uint256 i = 0; i < studentAddrs.length; i++) {
            students[studentAddrs[i]].karma += karmas[i];
        }
    }

    // --- Karma transfer function ---
    function transferKarma(address to, uint256 amount) public {
        require(students[msg.sender].karma >= amount, "Insufficient karma");
        students[msg.sender].karma -= amount;
        students[to].karma += amount;
        emit KarmaTransferred(msg.sender, to, amount);
    }

    // --- Read functions ---
    function getStudentData(address student) public view returns (
        uint256 grade,
        uint256 hackathonWins,
        uint256 healthHB,
        uint256 karma
    ) {
        Student storage s = students[student];
        return (s.grade, s.hackathonWins, s.healthHB, s.karma);
    }

    function getKarma(address student) public view returns (uint256) {
        return students[student].karma;
    }
}
