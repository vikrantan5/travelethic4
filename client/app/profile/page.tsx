"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  User,
  Mail,
  Calendar,
  CreditCard,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  Sparkles,
  ArrowLeft,
  Loader2,
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { getAuthToken } from "@/lib/auth";

interface PaymentTransaction {
  id: number;
  razorpay_order_id: string;
  razorpay_payment_id: string | null;
  amount: number;
  currency: string;
  plan_type: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

interface UserStats {
  has_used_free_planner: boolean;
  total_planners_created: number;
  is_premium: boolean;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [transactions, setTransactions] = useState<PaymentTransaction[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/auth");
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      fetchUserData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const fetchUserData = async () => {
    setLoadingData(true);
    try {
      const token = getAuthToken();
      const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.REACT_APP_BACKEND_URL + "/api";

      const transactionsResponse = await fetch(`${API_URL}/payment/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (transactionsResponse.ok) {
        const transactionsData = await transactionsResponse.json();
        setTransactions(transactionsData.transactions || []);
      }

      const statsResponse = await fetch(`${API_URL}/payment/user-stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setUserStats(statsData.stats);
      }
    } catch (error) {
      console.error("Error fetching user data:", error);
      toast.error("Failed to load profile data");
    } finally {
      setLoadingData(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatAmount = (amount: number, currency: string = "INR") => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: currency,
    }).format(amount / 100);
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "success":
      case "completed":
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case "failed":
        return <XCircle className="w-4 h-4 text-red-400" />;
      case "pending":
        return <Clock className="w-4 h-4 text-yellow-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    const cls =
      s === "success" || s === "completed"
        ? "bg-green-500/20 text-green-300 border border-green-500/30"
        : s === "failed"
        ? "bg-red-500/20 text-red-300 border border-red-500/30"
        : s === "pending"
        ? "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30"
        : "bg-gray-500/20 text-gray-300 border border-gray-500/30";
    return <Badge className={`capitalize ${cls}`}>{status}</Badge>;
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-400" />
          <p className="text-gray-300">Loading profile...</p>
        </div>
      </div>
    );
  }

  // Shared card styles to match team/compare/plans pages
  const cardClass =
    "bg-gray-800/50 border border-gray-700 backdrop-blur-sm text-gray-100 shadow-xl";
  const innerBlockClass =
    "p-4 bg-gray-900/40 border border-gray-700/60 rounded-lg";

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-8 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative glows */}
      <div className="absolute top-20 right-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-5xl mx-auto relative">
        {/* Header */}
        <div className="mb-8">
          <Link href="/plans">
            <Button
              variant="ghost"
              size="sm"
              className="mb-4 text-gray-300 hover:text-white hover:bg-gray-800/50"
              data-testid="profile-back-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Plans
            </Button>
          </Link>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            My Profile
          </h1>
          <p className="text-gray-400 mt-1">
            Manage your account and view subscription details
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {/* User Information Card */}
          <Card className={`md:col-span-2 ${cardClass}`} data-testid="profile-info-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <User className="w-5 h-5 text-purple-400" />
                Account Information
              </CardTitle>
              <CardDescription className="text-gray-400">
                Your personal details
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-4 p-4 bg-gray-900/40 border border-gray-700/60 rounded-lg">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shrink-0">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <h3 className="text-xl font-semibold text-white">{user.name}</h3>
                    {user.is_premium && (
                      <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white border-0">
                        <Sparkles className="w-3 h-3 mr-1" />
                        Premium
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-gray-300 mb-1">
                    <Mail className="w-4 h-4 text-purple-400" />
                    <span className="text-sm">{user.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <Calendar className="w-4 h-4 text-purple-400" />
                    <span className="text-sm">
                      Member since{" "}
                      {new Date(user.created_at).toLocaleDateString("en-US", {
                        month: "long",
                        year: "numeric",
                      })}
                    </span>
                  </div>
                </div>
              </div>

              <Separator className="bg-gray-700" />

              <div className="grid grid-cols-2 gap-4">
                <div className={innerBlockClass}>
                  <p className="text-sm text-gray-400 mb-1">Subscription Type</p>
                  <p className="text-lg font-semibold capitalize text-white">
                    {user.subscription_type || "Free"}
                  </p>
                </div>
                <div className={innerBlockClass}>
                  <p className="text-sm text-gray-400 mb-1">Account Status</p>
                  <p className="text-lg font-semibold text-green-400">Active</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats Card */}
          <Card className={cardClass} data-testid="profile-stats-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingData ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-purple-400" />
                </div>
              ) : userStats ? (
                <>
                  <div className="p-4 bg-gradient-to-br from-blue-900/30 to-indigo-900/30 rounded-lg border border-blue-800/50">
                    <p className="text-sm text-gray-400 mb-1">Total Plans Created</p>
                    <p className="text-3xl font-bold text-blue-300">
                      {userStats.total_planners_created}
                    </p>
                  </div>

                  <div className={innerBlockClass}>
                    <p className="text-sm text-gray-400 mb-2">Free Planner Used</p>
                    <div className="flex items-center gap-2">
                      {userStats.has_used_free_planner ? (
                        <>
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                          <span className="text-sm font-medium text-white">Yes</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-4 h-4 text-gray-400" />
                          <span className="text-sm font-medium text-white">Not yet</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className={innerBlockClass}>
                    <p className="text-sm text-gray-400 mb-2">Premium Status</p>
                    <div className="flex items-center gap-2">
                      {userStats.is_premium ? (
                        <>
                          <Sparkles className="w-4 h-4 text-yellow-400" />
                          <span className="text-sm font-medium text-white">Active</span>
                        </>
                      ) : (
                        <span className="text-sm font-medium text-white">Not Active</span>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-sm text-gray-400 text-center py-4">
                  No stats available
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Subscription History */}
        <Card className={`mt-6 ${cardClass}`} data-testid="profile-history-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <CreditCard className="w-5 h-5 text-purple-400" />
              Subscription History
            </CardTitle>
            <CardDescription className="text-gray-400">
              View your payment transactions and subscription details
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loadingData ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
              </div>
            ) : transactions.length > 0 ? (
              <div className="space-y-4">
                {transactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-start justify-between p-4 bg-gray-900/40 rounded-lg border border-gray-700/60 hover:border-purple-500/40 hover:bg-gray-900/60 transition-colors"
                  >
                    <div className="flex items-start gap-3 flex-1">
                      {getStatusIcon(transaction.status)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <h4 className="font-semibold text-sm text-white">
                            {transaction.plan_type
                              ? `${transaction.plan_type} Plan`
                              : "Payment"}
                          </h4>
                          {getStatusBadge(transaction.status)}
                        </div>
                        <p className="text-xs text-gray-400 mb-1 break-all">
                          Order ID: {transaction.razorpay_order_id}
                        </p>
                        {transaction.razorpay_payment_id && (
                          <p className="text-xs text-gray-400 break-all">
                            Payment ID: {transaction.razorpay_payment_id}
                          </p>
                        )}
                        <p className="text-xs text-gray-400 mt-2">
                          <Clock className="w-3 h-3 inline mr-1" />
                          {formatDate(transaction.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <p className="font-bold text-lg text-white whitespace-nowrap">
                        {formatAmount(transaction.amount, transaction.currency)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <CreditCard className="w-12 h-12 text-gray-500 mx-auto mb-4 opacity-60" />
                <h3 className="text-lg font-semibold mb-2 text-white">
                  No Subscription History
                </h3>
                <p className="text-sm text-gray-400 mb-4">
                  You haven&apos;t made any payments yet.
                </p>
                <Link href="/plan">
                  <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Create Your First Plan
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Upgrade to Premium CTA */}
        {!user.is_premium && (
          <Card
            className="mt-6 bg-gradient-to-br from-purple-900/40 to-blue-900/40 border border-purple-700/50 text-gray-100 backdrop-blur-sm"
            data-testid="profile-upgrade-card"
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div>
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2 text-white">
                    <Sparkles className="w-5 h-5 text-yellow-400" />
                    Upgrade to Premium
                  </h3>
                  <p className="text-gray-300 mb-4">
                    Unlock unlimited trip planning and premium features
                  </p>
                </div>
                <Link href="/plan">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    Upgrade Now
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
