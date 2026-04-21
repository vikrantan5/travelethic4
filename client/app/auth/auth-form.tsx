"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Label } from "@/components/ui/label";
import { motion } from "framer-motion";

export default function AuthForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const router = useRouter();
  const { login, register } = useAuth();

  function handleInputChange(field: string, value: string) {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }

  // Hard-navigate so the newly-set auth_token cookie is picked up by
  // Next.js middleware (matcher: /plan, /plans). router.push() sometimes
  // races the cookie write and the middleware redirects back to /auth.
  const redirectToDashboard = () => {
    if (typeof window !== "undefined") {
      window.location.href = "/plan";
    } else {
      router.push("/plan");
    }
  };

  async function handleSignIn(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(formData.email, formData.password);
      toast.success("Welcome back! Redirecting to your dashboard...");
      redirectToDashboard();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to sign in";
      toast.error(message);
      console.error("Sign in failed:", error);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSignUp(e: React.FormEvent) {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error("Please enter your name");
      return;
    }

    if (!formData.email.trim()) {
      toast.error("Please enter your email");
      return;
    }

    if (formData.password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setIsLoading(true);

    try {
      await register(formData.email, formData.password, formData.name);
      toast.success("Account created successfully! Redirecting...");
      redirectToDashboard();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to create account";
      toast.error(message);
      console.error("Sign up failed:", error);
    } finally {
      setIsLoading(false);
    }
  }

  // Shared input / label styling so text is visible on the light card
  const labelClass = "text-gray-900 font-medium";
  const inputClass =
    "text-gray-900 placeholder:text-gray-400 bg-white border-gray-300 focus-visible:ring-purple-500";

  return (
    <motion.div
      className="flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900/30 to-gray-900 px-4 py-8 md:min-h-screen md:py-0 relative overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Decorative glows to match other pages */}
      <div className="absolute top-20 right-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="w-full max-w-md relative"
      >
        <Card className="w-full border border-purple-200/60 shadow-2xl bg-gradient-to-br from-teal-50 via-purple-50 to-teal-50 backdrop-blur-sm text-gray-900">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Welcome to Travelethic
            </CardTitle>
            <CardDescription className="text-center text-gray-700">
              Sign in to your account or create a new one
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="signin" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger
                  value="signin"
                  className="data-[state=active]:text-white text-gray-500"
                  data-testid="auth-tab-signin"
                >
                  Sign In
                </TabsTrigger>
                <TabsTrigger
                  value="signup"
                  className="data-[state=active]:text-white text-gray-500"
                  data-testid="auth-tab-signup"
                >
                  Sign Up
                </TabsTrigger>
              </TabsList>

              <TabsContent value="signin">
                <motion.form
                  onSubmit={handleSignIn}
                  className="space-y-4 pt-2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4 }}
                >
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.1 }}
                  >
                    <Label className={labelClass} htmlFor="signin-email">
                      Email
                    </Label>
                    <Input
                      className={inputClass}
                      id="signin-email"
                      type="email"
                      placeholder="you@example.com"
                      value={formData.email}
                      onChange={(e) => handleInputChange("email", e.target.value)}
                      required
                      disabled={isLoading}
                      data-testid="signin-email-input"
                    />
                  </motion.div>
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 }}
                  >
                    <Label className={labelClass} htmlFor="signin-password">
                      Password
                    </Label>
                    <Input
                      className={inputClass}
                      id="signin-password"
                      type="password"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) =>
                        handleInputChange("password", e.target.value)
                      }
                      required
                      disabled={isLoading}
                      data-testid="signin-password-input"
                    />
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.3 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      type="submit"
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all text-white"
                      disabled={isLoading}
                      data-testid="signin-submit-btn"
                    >
                      {isLoading ? "Signing in..." : "Sign In"}
                    </Button>
                  </motion.div>
                </motion.form>
              </TabsContent>

              <TabsContent value="signup">
                <motion.form
                  onSubmit={handleSignUp}
                  className="space-y-4 pt-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4 }}
                >
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.1 }}
                  >
                    <Label className={labelClass} htmlFor="signup-name">
                      Name
                    </Label>
                    <Input
                      className={inputClass}
                      id="signup-name"
                      type="text"
                      placeholder="John Doe"
                      value={formData.name}
                      onChange={(e) => handleInputChange("name", e.target.value)}
                      required
                      disabled={isLoading}
                      data-testid="signup-name-input"
                    />
                  </motion.div>
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 }}
                  >
                    <Label className={labelClass} htmlFor="signup-email">
                      Email
                    </Label>
                    <Input
                      className={inputClass}
                      id="signup-email"
                      type="email"
                      placeholder="you@example.com"
                      value={formData.email}
                      onChange={(e) => handleInputChange("email", e.target.value)}
                      required
                      disabled={isLoading}
                      data-testid="signup-email-input"
                    />
                  </motion.div>
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.3 }}
                  >
                    <Label className={labelClass} htmlFor="signup-password">
                      Password
                    </Label>
                    <Input
                      className={inputClass}
                      id="signup-password"
                      type="password"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) =>
                        handleInputChange("password", e.target.value)
                      }
                      required
                      disabled={isLoading}
                      minLength={6}
                      data-testid="signup-password-input"
                    />
                    <p className="text-xs text-gray-700">
                      Password must be at least 6 characters
                    </p>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.4 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      type="submit"
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all text-white"
                      disabled={isLoading}
                      data-testid="signup-submit-btn"
                    >
                      {isLoading ? "Creating account..." : "Sign Up"}
                    </Button>
                  </motion.div>
                </motion.form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
