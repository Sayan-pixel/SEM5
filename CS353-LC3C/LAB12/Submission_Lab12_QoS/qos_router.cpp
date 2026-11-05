/**
 * CS353: Quality of Service (QoS) at a Router
 * Implementation in C++ (C++17)
 * 
 * Implements:
 * 1. Admission Control (Parekh-Gallagher Test)
 * 2. Traffic Policing (Token Bucket Drop)
 * 3. Traffic Shaping (Token Bucket Buffer & Smooth)
 * 4. Packet Scheduling (Weighted Fair Queuing vs FIFO)
 */

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include <cmath>
#include <cassert>
#include <map>

// =====================================================================
// Data Structures
// =====================================================================

struct FlowRequest {
    std::string flow;
    double weight;
    double rate;
};

struct AdmissionDecision {
    std::string flow;
    double weight;
    double rate;
    bool admitted;
    double totalWeight;
    double guaranteedRate;
    std::string reason;
};

struct PoliceResult {
    int packetIndex;
    double arrivalTime;
    double tokensBefore;
    std::string action; // "PASS" or "DROP"
    double tokensAfter;
};

struct ShapeResult {
    int packetIndex;
    double arrivalTime;
    double releaseTime;
    double delay;
};

struct Packet {
    std::string name;
    double arrival;
    double length;
};

struct Flow {
    std::string name;
    double weight;
    std::vector<Packet> packets;
};

struct ScheduledPacket {
    std::string name;
    std::string flow;
    double weight;
    double arrival;
    double length;
    double finishNumber;
};

// =====================================================================
// Required Interfaces
// =====================================================================

// Part A: Admission Control
std::vector<AdmissionDecision> admit(const std::vector<FlowRequest>& requests, double C) {
    std::vector<FlowRequest> admittedFlows;
    std::vector<AdmissionDecision> decisions;

    for (const auto& req : requests) {
        std::vector<FlowRequest> candidateFlows = admittedFlows;
        candidateFlows.push_back(req);

        double totalWeight = 0.0;
        for (const auto& f : candidateFlows) {
            totalWeight += f.weight;
        }

        bool allSatisfied = true;
        double reqGuaranteedRate = 0.0;

        for (const auto& f : candidateFlows) {
            double guaranteed = (f.weight / totalWeight) * C;
            if (f.flow == req.flow) {
                reqGuaranteedRate = guaranteed;
            }
            if (guaranteed < f.rate - 1e-9) {
                allSatisfied = false;
            }
        }

        AdmissionDecision decision;
        decision.flow = req.flow;
        decision.weight = req.weight;
        decision.rate = req.rate;
        decision.totalWeight = totalWeight;
        decision.guaranteedRate = reqGuaranteedRate;

        if (allSatisfied) {
            admittedFlows = candidateFlows;
            decision.admitted = true;
            decision.reason = "Guaranteed rate >= requested rate; previous guarantees preserved.";
        } else {
            decision.admitted = false;
            decision.reason = "Guaranteed rate < requested rate (or violates existing flow guarantee).";
        }
        decisions.push_back(decision);
    }

    return decisions;
}

// Part B: Traffic Policing
std::vector<PoliceResult> police(const std::vector<double>& trace, double r, double b, double packetSize = 1.0) {
    double tokens = b; // bucket starts full
    double lastTime = trace.empty() ? 0.0 : trace[0];
    std::vector<PoliceResult> results;

    for (size_t i = 0; i < trace.size(); ++i) {
        double t = trace[i];
        double dt = std::max(0.0, t - lastTime);
        tokens = std::min(b, tokens + dt * r);
        lastTime = t;

        PoliceResult res;
        res.packetIndex = static_cast<int>(i + 1);
        res.arrivalTime = t;
        res.tokensBefore = tokens;

        if (tokens >= packetSize) {
            tokens -= packetSize;
            res.action = "PASS";
        } else {
            res.action = "DROP";
        }
        res.tokensAfter = tokens;
        results.push_back(res);
    }

    return results;
}

// Part C: Traffic Shaping
std::vector<ShapeResult> shape(const std::vector<double>& trace, double r, double b, double packetSize = 1.0) {
    double tokens = b; // bucket starts full
    double currentTime = trace.empty() ? 0.0 : trace[0];
    std::vector<ShapeResult> results;

    for (size_t i = 0; i < trace.size(); ++i) {
        double t = trace[i];
        if (t > currentTime) {
            double dt = t - currentTime;
            tokens = std::min(b, tokens + dt * r);
            currentTime = t;
        }

        double releaseTime = 0.0;
        if (tokens >= packetSize) {
            tokens -= packetSize;
            releaseTime = currentTime;
        } else {
            double needed = packetSize - tokens;
            double waitTime = needed / r;
            currentTime += waitTime;
            tokens = 0.0;
            releaseTime = currentTime;
        }

        ShapeResult res;
        res.packetIndex = static_cast<int>(i + 1);
        res.arrivalTime = t;
        res.releaseTime = releaseTime;
        res.delay = releaseTime - t;
        results.push_back(res);
    }

    return results;
}

// Part D: Weighted Fair Queuing (WFQ)
std::pair<std::map<std::string, double>, std::vector<std::string>> wfq(const std::vector<Flow>& flows) {
    std::map<std::string, double> finishNumbers;
    std::vector<ScheduledPacket> allPackets;

    for (const auto& flow : flows) {
        double prevFinish = 0.0;
        for (const auto& pkt : flow.packets) {
            double startTime = std::max(pkt.arrival, prevFinish);
            double finishTime = startTime + (pkt.length / flow.weight);
            prevFinish = finishTime;

            finishNumbers[pkt.name] = finishTime;
            allPackets.push_back({pkt.name, flow.name, flow.weight, pkt.arrival, pkt.length, finishTime});
        }
    }

    std::sort(allPackets.begin(), allPackets.end(), [](const ScheduledPacket& a, const ScheduledPacket& b) {
        if (std::abs(a.finishNumber - b.finishNumber) > 1e-9) {
            return a.finishNumber < b.finishNumber;
        }
        if (std::abs(a.arrival - b.arrival) > 1e-9) {
            return a.arrival < b.arrival;
        }
        return a.name < b.name;
    });

    std::vector<std::string> outputOrder;
    for (const auto& p : allPackets) {
        outputOrder.push_back(p.name);
    }

    return {finishNumbers, outputOrder};
}

// Part D: First-In First-Out (FIFO)
std::vector<std::string> fifo(const std::vector<Flow>& flows) {
    struct RawPacket {
        std::string name;
        double arrival;
        size_t flowIndex;
        size_t packetIndex;
    };

    std::vector<RawPacket> allPackets;
    for (size_t f = 0; f < flows.size(); ++f) {
        for (size_t p = 0; p < flows[f].packets.size(); ++p) {
            allPackets.push_back({flows[f].packets[p].name, flows[f].packets[p].arrival, f, p});
        }
    }

    std::stable_sort(allPackets.begin(), allPackets.end(), [](const RawPacket& a, const RawPacket& b) {
        return a.arrival < b.arrival;
    });

    std::vector<std::string> order;
    for (const auto& p : allPackets) {
        order.push_back(p.name);
    }
    return order;
}

// =====================================================================
// Demonstration & Test Harness
// =====================================================================

int main() {
    std::cout << std::string(78, '=') << "\n";
    std::cout << "CS353 NETWORK QoS ROUTER: C++ SIMULATION & VERIFICATION\n";
    std::cout << std::string(78, '=') << "\n\n";

    // -------------------------------------------------------------
    // Part A
    // -------------------------------------------------------------
    std::cout << std::string(78, '#') << "\n";
    std::cout << "PART A: ADMISSION CONTROL\n";
    std::cout << std::string(78, '#') << "\n";
    double C = 10.0;
    std::vector<FlowRequest> requests = {
        {"f1", 1.0, 2.0},
        {"f2", 1.0, 2.0},
        {"f3", 2.0, 4.0},
        {"f4", 1.0, 3.0}
    };

    auto decisions = admit(requests, C);
    std::cout << std::left << std::setw(6) << "Flow"
              << std::setw(10) << "Req Rate"
              << std::setw(10) << "Total W"
              << std::setw(14) << "Guaranteed"
              << std::setw(12) << "Decision"
              << "Reason\n";
    std::cout << std::string(70, '-') << "\n";
    for (const auto& d : decisions) {
        std::cout << std::left << std::setw(6) << d.flow
                  << std::setw(10) << std::fixed << std::setprecision(1) << d.rate
                  << std::setw(10) << d.totalWeight
                  << std::setw(14) << std::setprecision(2) << d.guaranteedRate
                  << std::setw(12) << (d.admitted ? "ADMITTED" : "REJECTED")
                  << d.reason << "\n";
    }

    assert(decisions[0].admitted == true);
    assert(decisions[1].admitted == true);
    assert(decisions[2].admitted == true);
    assert(decisions[3].admitted == false);
    std::cout << "\n[CONFIRMED] f1, f2, f3 admitted; f4 rejected (guaranteed 2.0 Mbps < 3.0 Mbps requested).\n\n";

    // -------------------------------------------------------------
    // Part B
    // -------------------------------------------------------------
    std::cout << std::string(78, '#') << "\n";
    std::cout << "PART B: TRAFFIC POLICING\n";
    std::cout << std::string(78, '#') << "\n";
    double r = 1.0;
    double b = 4.0;
    std::vector<double> trace = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 6.0};

    auto pol = police(trace, r, b);
    std::cout << std::left << std::setw(8) << "Pkt #"
              << std::setw(10) << "Arrival"
              << std::setw(16) << "Tokens Before"
              << std::setw(10) << "Action"
              << "Tokens After\n";
    std::cout << std::string(58, '-') << "\n";
    int passCount = 0, dropCount = 0;
    for (const auto& p : pol) {
        std::cout << std::left << std::setw(8) << p.packetIndex
                  << std::setw(10) << std::fixed << std::setprecision(1) << p.arrivalTime
                  << std::setw(16) << std::setprecision(2) << p.tokensBefore
                  << std::setw(10) << p.action
                  << p.tokensAfter << "\n";
        if (p.action == "PASS") passCount++; else dropCount++;
    }
    assert(passCount == 6 && dropCount == 2);
    std::cout << "\n[CONFIRMED] " << passCount << " passed, " << dropCount << " dropped.\n\n";

    // -------------------------------------------------------------
    // Part C
    // -------------------------------------------------------------
    std::cout << std::string(78, '#') << "\n";
    std::cout << "PART C: TRAFFIC SHAPING\n";
    std::cout << std::string(78, '#') << "\n";
    auto shp = shape(trace, r, b);
    std::cout << std::left << std::setw(8) << "Pkt #"
              << std::setw(10) << "Arrival"
              << std::setw(16) << "Release Time"
              << std::setw(10) << "Delay"
              << "Status\n";
    std::cout << std::string(56, '-') << "\n";
    std::vector<double> expRelease = {0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 5.0, 6.0};
    for (size_t i = 0; i < shp.size(); ++i) {
        std::cout << std::left << std::setw(8) << shp[i].packetIndex
                  << std::setw(10) << std::fixed << std::setprecision(1) << shp[i].arrivalTime
                  << std::setw(16) << shp[i].releaseTime
                  << std::setw(10) << shp[i].delay
                  << "DELIVERED\n";
        assert(std::abs(shp[i].releaseTime - expRelease[i]) < 1e-6);
    }
    std::cout << "\n[CONFIRMED] Release times exactly match 0, 0, 0, 0, 1, 2, 5, 6.\n\n";

    // -------------------------------------------------------------
    // Part D
    // -------------------------------------------------------------
    std::cout << std::string(78, '#') << "\n";
    std::cout << "PART D: WEIGHTED FAIR QUEUING (WFQ) VS FIFO\n";
    std::cout << std::string(78, '#') << "\n";
    std::vector<Flow> flows = {
        {"Flow 1", 1.0, {{"A", 0.0, 8.0}, {"F", 10.0, 6.0}}},
        {"Flow 2", 1.0, {{"B", 5.0, 6.0}, {"D", 8.0, 9.0}, {"H", 20.0, 8.0}}},
        {"Flow 3", 2.0, {{"C", 5.0, 10.0}, {"E", 8.0, 8.0}, {"G", 11.0, 10.0}}}
    };

    auto [fnums, wfqOrder] = wfq(flows);
    auto fifoOrder = fifo(flows);

    std::cout << "Computed WFQ Finish Numbers:\n";
    for (const auto& [name, num] : fnums) {
        std::cout << "  Packet " << name << " -> F = " << num << "\n";
    }

    std::cout << "\nWFQ Output Order:  ";
    for (size_t i = 0; i < wfqOrder.size(); ++i) {
        std::cout << wfqOrder[i] << (i + 1 < wfqOrder.size() ? " -> " : "\n");
    }

    std::cout << "FIFO Arrival Order: ";
    for (size_t i = 0; i < fifoOrder.size(); ++i) {
        std::cout << fifoOrder[i] << (i + 1 < fifoOrder.size() ? " -> " : "\n");
    }

    std::vector<std::string> expWfqOrder = {"A", "C", "B", "E", "F", "G", "D", "H"};
    assert(wfqOrder == expWfqOrder);
    std::cout << "\n[CONFIRMED] WFQ order exactly matches A, C, B, E, F, G, D, H.\n";
    std::cout << std::string(78, '=') << "\n";
    std::cout << "ALL C++ TESTS PASSED SUCCESSFULLY!\n";
    std::cout << std::string(78, '=') << "\n";

    return 0;
}

