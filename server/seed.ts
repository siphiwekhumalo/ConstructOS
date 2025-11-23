import { storage } from "./storage";

export async function seedDatabase() {
  console.log("Seeding database...");

  // Seed projects
  const projectsData = [
    {
      name: "Skyline Office Complex",
      location: "Downtown Metro",
      status: "In Progress",
      progress: 65,
      budget: "12500000",
      dueDate: "Dec 2025",
    },
    {
      name: "Riverside Residential",
      location: "North District",
      status: "Planning",
      progress: 15,
      budget: "4200000",
      dueDate: "Mar 2026",
    },
    {
      name: "Industrial Warehouse A",
      location: "Logistics Park",
      status: "Delayed",
      progress: 88,
      budget: "8100000",
      dueDate: "Oct 2025",
    },
    {
      name: "City Bridge Renovation",
      location: "South Bridge",
      status: "Completed",
      progress: 100,
      budget: "2500000",
      dueDate: "Sep 2025",
    },
  ];

  for (const project of projectsData) {
    try {
      await storage.createProject(project);
    } catch (error) {
      console.log("Project already exists or error:", error);
    }
  }

  // Seed equipment
  const equipmentData = [
    {
      name: "Excavator CAT 320",
      status: "Active",
      location: "Site A",
      nextService: "15 Days",
      imageUrl: "https://images.unsplash.com/photo-1586118293331-92a37b211093?q=80&w=300&auto=format&fit=crop",
    },
    {
      name: "Tower Crane TC-50",
      status: "Maintenance",
      location: "Site B",
      nextService: "Overdue",
      imageUrl: "https://images.unsplash.com/photo-1541625602330-2277a4c46182?q=80&w=300&auto=format&fit=crop",
    },
    {
      name: "Bulldozer D6T",
      status: "Active",
      location: "Site A",
      nextService: "45 Days",
      imageUrl: "https://images.unsplash.com/photo-1527199768775-bdabf8b3b158?q=80&w=300&auto=format&fit=crop",
    },
  ];

  for (const item of equipmentData) {
    try {
      await storage.createEquipment(item);
    } catch (error) {
      console.log("Equipment already exists or error:", error);
    }
  }

  // Seed clients
  const clientsData = [
    {
      name: "Alice Freeman",
      company: "Skyline Developers",
      role: "Project Owner",
      email: "alice@skylinedev.com",
      phone: "+1 (555) 123-4567",
      status: "Active Negotiation",
      avatar: "AF",
    },
    {
      name: "Robert Chen",
      company: "City Planning Dept",
      role: "Civil Engineer",
      email: "r.chen@cityplanning.gov",
      phone: "+1 (555) 987-6543",
      status: "Contract Signed",
      avatar: "RC",
    },
    {
      name: "Sarah Miller",
      company: "Miller Investments",
      role: "Lead Investor",
      email: "sarah@millerinv.com",
      phone: "+1 (555) 456-7890",
      status: "Proposal Sent",
      avatar: "SM",
    },
  ];

  for (const client of clientsData) {
    try {
      await storage.createClient(client);
    } catch (error) {
      console.log("Client already exists or error:", error);
    }
  }

  // Seed transactions
  const transactionsData = [
    {
      projectId: null,
      description: "Steel Supply Co.",
      amount: "45000",
      status: "Pending",
      date: new Date(),
    },
    {
      projectId: null,
      description: "Heavy Machinery Rentals",
      amount: "12500",
      status: "Paid",
      date: new Date(Date.now() - 86400000),
    },
    {
      projectId: null,
      description: "City Concrete Mixers",
      amount: "8200",
      status: "Paid",
      date: new Date(Date.now() - 172800000),
    },
  ];

  for (const transaction of transactionsData) {
    try {
      await storage.createTransaction(transaction);
    } catch (error) {
      console.log("Transaction already exists or error:", error);
    }
  }

  console.log("Database seeded successfully!");
}
