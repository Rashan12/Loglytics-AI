"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  CreditCard, 
  Download, 
  Calendar, 
  DollarSign,
  FileText,
  Edit,
  CheckCircle,
  AlertCircle,
  Clock
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { InvoiceTable } from "./InvoiceTable"
import { useSettingsStore } from "@/store/settings-store"
import { useUIStore } from "@/store/ui-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function BillingTab() {
  const { addToast } = useUIStore()
  const {
    billingInfo,
    subscription,
    isLoading,
    updatePaymentMethod
  } = useSettingsStore()

  const [showEditPayment, setShowEditPayment] = React.useState(false)
  const [showEditBilling, setShowEditBilling] = React.useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <Badge variant="default" className="flex items-center gap-1"><CheckCircle className="h-3 w-3" />Paid</Badge>
      case 'pending':
        return <Badge variant="secondary" className="flex items-center gap-1"><Clock className="h-3 w-3" />Pending</Badge>
      case 'failed':
        return <Badge variant="destructive" className="flex items-center gap-1"><AlertCircle className="h-3 w-3" />Failed</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const handleDownloadInvoice = (invoiceId: string) => {
    // Simulate invoice download
    addToast({
      title: "Invoice Downloaded",
      description: "Your invoice has been downloaded successfully.",
      type: "success"
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Billing</h2>
        <p className="text-muted-foreground">
          Manage your payment methods and billing history
        </p>
      </div>

      {/* Payment Method */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Payment Method
            </CardTitle>
            <CardDescription>
              Your current payment method for subscription billing
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {billingInfo?.payment_method ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
                      <CreditCard className="h-5 w-5" />
                    </div>
                    <div className="space-y-1">
                      <p className="font-medium">
                        {billingInfo.payment_method.brand.toUpperCase()} •••• {billingInfo.payment_method.last4}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Expires {billingInfo.payment_method.expiry_month}/{billingInfo.payment_method.expiry_year}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowEditPayment(true)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Update
                  </Button>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label>Billing Address</Label>
                  <div className="p-3 bg-muted rounded-lg text-sm">
                    <p className="font-medium">{billingInfo.billing_address.name}</p>
                    <p>{billingInfo.billing_address.line1}</p>
                    {billingInfo.billing_address.line2 && <p>{billingInfo.billing_address.line2}</p>}
                    <p>
                      {billingInfo.billing_address.city}, {billingInfo.billing_address.state} {billingInfo.billing_address.postal_code}
                    </p>
                    <p>{billingInfo.billing_address.country}</p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowEditBilling(true)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Address
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                  <CreditCard className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Payment Method</h3>
                <p className="text-muted-foreground mb-4">
                  Add a payment method to manage your subscription
                </p>
                <Button onClick={() => setShowEditPayment(true)}>
                  <CreditCard className="h-4 w-4 mr-2" />
                  Add Payment Method
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Billing History */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Billing History
            </CardTitle>
            <CardDescription>
              Your past invoices and payment history
            </CardDescription>
          </CardHeader>
          <CardContent>
            {billingInfo?.invoices && billingInfo.invoices.length > 0 ? (
              <InvoiceTable
                invoices={billingInfo.invoices}
                onDownload={handleDownloadInvoice}
              />
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Billing History</h3>
                <p className="text-muted-foreground">
                  Your billing history will appear here
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Upcoming Invoice */}
      {subscription && (
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Upcoming Invoice
              </CardTitle>
              <CardDescription>
                Details about your next billing cycle
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Next Charge</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(subscription.current_period_end)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold">$29.00</p>
                  <p className="text-sm text-muted-foreground">Pro Subscription</p>
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Pro Subscription</span>
                  <span>$29.00</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Tax</span>
                  <span>$0.00</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between font-medium">
                  <span>Total</span>
                  <span>$29.00</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Usage-Based Pricing */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Current Month Usage
            </CardTitle>
            <CardDescription>
              Your usage and charges for the current billing period
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">LLM Tokens</span>
                  <span className="text-sm text-muted-foreground">Unlimited</span>
                </div>
                <div className="text-2xl font-bold">
                  {subscription?.usage.llm_tokens_used.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">tokens used</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Storage</span>
                  <span className="text-sm text-muted-foreground">100GB limit</span>
                </div>
                <div className="text-2xl font-bold">
                  {subscription?.usage.storage_used_gb || 0}GB
                </div>
                <p className="text-xs text-muted-foreground">used</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">API Calls</span>
                  <span className="text-sm text-muted-foreground">Unlimited</span>
                </div>
                <div className="text-2xl font-bold">
                  {subscription?.usage.api_calls.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">calls made</p>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Current Month Charges</span>
                <span className="font-bold">$29.00</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Fixed monthly subscription fee
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Edit Payment Method Dialog */}
      {showEditPayment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Update Payment Method</CardTitle>
              <CardDescription>
                Update your payment method for subscription billing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Card Number</Label>
                <Input placeholder="1234 5678 9012 3456" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Expiry Date</Label>
                  <Input placeholder="MM/YY" />
                </div>
                <div className="space-y-2">
                  <Label>CVC</Label>
                  <Input placeholder="123" />
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1" onClick={() => setShowEditPayment(false)}>
                  Cancel
                </Button>
                <Button className="flex-1">Update</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Edit Billing Address Dialog */}
      {showEditBilling && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Edit Billing Address</CardTitle>
              <CardDescription>
                Update your billing address information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Full Name</Label>
                <Input placeholder="John Doe" />
              </div>
              <div className="space-y-2">
                <Label>Address Line 1</Label>
                <Input placeholder="123 Main St" />
              </div>
              <div className="space-y-2">
                <Label>Address Line 2</Label>
                <Input placeholder="Apt 4B" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>City</Label>
                  <Input placeholder="New York" />
                </div>
                <div className="space-y-2">
                  <Label>State</Label>
                  <Input placeholder="NY" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Postal Code</Label>
                  <Input placeholder="10001" />
                </div>
                <div className="space-y-2">
                  <Label>Country</Label>
                  <Input placeholder="United States" />
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1" onClick={() => setShowEditBilling(false)}>
                  Cancel
                </Button>
                <Button className="flex-1">Update</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
