import { Router } from "express";
import powerbiRoutes from "./powerbi";
import authRoutes from "./auth";
import { rateLimit } from "../../services/api-gateway";

const router = Router();

router.use("/powerbi", rateLimit("powerbi"), powerbiRoutes);
router.use("/auth", rateLimit("auth"), authRoutes);

export default router;
