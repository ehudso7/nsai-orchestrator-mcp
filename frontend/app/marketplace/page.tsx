"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import {
  Search,
  Filter,
  Star,
  Download,
  Eye,
  Clock,
  DollarSign,
  TrendingUp,
  Package,
  Sparkles,
  ChevronRight,
  Heart,
  Share2,
  Code,
  Database,
  Globe,
  Zap,
  Brain,
  BarChart,
  FileText,
  Shield,
  Users,
  Tag,
  Plus,
  Upload
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface WorkflowTemplate {
  id: string;
  uuid: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  author: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  price_usd: number;
  downloads_count: number;
  rating: number;
  rating_count: number;
  tags: string[];
  preview_image_url?: string;
  created_at: string;
  nodes_count: number;
  estimated_run_time: string;
}

const categoryIcons: Record<string, any> = {
  "Data Analysis": BarChart,
  "Web Scraping": Globe,
  "Code Generation": Code,
  "AI Automation": Brain,
  "Database": Database,
  "Security": Shield,
  "Content Creation": FileText,
  "Integration": Zap,
};

const categories = [
  { name: "All", icon: Package, count: 0 },
  { name: "Data Analysis", icon: BarChart, count: 0 },
  { name: "Web Scraping", icon: Globe, count: 0 },
  { name: "Code Generation", icon: Code, count: 0 },
  { name: "AI Automation", icon: Brain, count: 0 },
  { name: "Database", icon: Database, count: 0 },
  { name: "Security", icon: Shield, count: 0 },
  { name: "Content Creation", icon: FileText, count: 0 },
  { name: "Integration", icon: Zap, count: 0 },
];

export default function MarketplacePage() {
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("popular");
  const [priceFilter, setPriceFilter] = useState("all");
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchTemplates();
    loadFavorites();
  }, []);

  useEffect(() => {
    filterAndSortTemplates();
  }, [templates, selectedCategory, searchQuery, sortBy, priceFilter]);

  const fetchTemplates = async () => {
    try {
      // For demo, use mock data
      const mockTemplates: WorkflowTemplate[] = [
        {
          id: "1",
          uuid: "template-1",
          name: "Advanced Data Pipeline",
          description: "Complete ETL pipeline with data validation, transformation, and analysis using multiple AI agents",
          category: "Data Analysis",
          icon: "database",
          author: { id: 1, username: "datamaster", avatar_url: "" },
          price_usd: 0,
          downloads_count: 1523,
          rating: 4.8,
          rating_count: 234,
          tags: ["ETL", "Data Processing", "Analytics"],
          created_at: new Date().toISOString(),
          nodes_count: 12,
          estimated_run_time: "5-10 min"
        },
        {
          id: "2",
          uuid: "template-2",
          name: "Smart Web Scraper Pro",
          description: "Intelligent web scraping with automatic pattern detection and data extraction",
          category: "Web Scraping",
          icon: "globe",
          author: { id: 2, username: "webscraper_pro", avatar_url: "" },
          price_usd: 4.99,
          downloads_count: 892,
          rating: 4.6,
          rating_count: 156,
          tags: ["Web Scraping", "Data Extraction", "Automation"],
          created_at: new Date().toISOString(),
          nodes_count: 8,
          estimated_run_time: "2-5 min"
        },
        {
          id: "3",
          uuid: "template-3",
          name: "AI Code Generator Suite",
          description: "Generate complete applications with tests, documentation, and deployment configs",
          category: "Code Generation",
          icon: "code",
          author: { id: 3, username: "ai_developer", avatar_url: "" },
          price_usd: 9.99,
          downloads_count: 2341,
          rating: 4.9,
          rating_count: 412,
          tags: ["Code Generation", "Testing", "Documentation"],
          created_at: new Date().toISOString(),
          nodes_count: 15,
          estimated_run_time: "10-15 min"
        },
        {
          id: "4",
          uuid: "template-4",
          name: "Content Creation Workflow",
          description: "Generate SEO-optimized articles with research, writing, and optimization agents",
          category: "Content Creation",
          icon: "file-text",
          author: { id: 4, username: "content_creator", avatar_url: "" },
          price_usd: 0,
          downloads_count: 3421,
          rating: 4.7,
          rating_count: 523,
          tags: ["Content", "SEO", "Writing"],
          created_at: new Date().toISOString(),
          nodes_count: 10,
          estimated_run_time: "5-8 min"
        },
        {
          id: "5",
          uuid: "template-5",
          name: "Security Audit Automation",
          description: "Comprehensive security scanning and vulnerability assessment workflow",
          category: "Security",
          icon: "shield",
          author: { id: 5, username: "security_expert", avatar_url: "" },
          price_usd: 14.99,
          downloads_count: 567,
          rating: 4.9,
          rating_count: 89,
          tags: ["Security", "Audit", "Compliance"],
          created_at: new Date().toISOString(),
          nodes_count: 20,
          estimated_run_time: "15-30 min"
        },
        {
          id: "6",
          uuid: "template-6",
          name: "Multi-Agent Research Assistant",
          description: "Coordinate multiple AI agents to conduct comprehensive research on any topic",
          category: "AI Automation",
          icon: "brain",
          author: { id: 6, username: "research_ai", avatar_url: "" },
          price_usd: 0,
          downloads_count: 4532,
          rating: 4.8,
          rating_count: 678,
          tags: ["Research", "Multi-Agent", "Analysis"],
          created_at: new Date().toISOString(),
          nodes_count: 18,
          estimated_run_time: "10-20 min"
        }
      ];

      setTemplates(mockTemplates);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load templates");
      setLoading(false);
    }
  };

  const loadFavorites = () => {
    const saved = localStorage.getItem("marketplace_favorites");
    if (saved) {
      setFavorites(new Set(JSON.parse(saved)));
    }
  };

  const toggleFavorite = (templateId: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(templateId)) {
      newFavorites.delete(templateId);
    } else {
      newFavorites.add(templateId);
    }
    setFavorites(newFavorites);
    localStorage.setItem("marketplace_favorites", JSON.stringify(Array.from(newFavorites)));
  };

  const filterAndSortTemplates = () => {
    let filtered = templates;

    // Category filter
    if (selectedCategory !== "All") {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Price filter
    if (priceFilter === "free") {
      filtered = filtered.filter(t => t.price_usd === 0);
    } else if (priceFilter === "paid") {
      filtered = filtered.filter(t => t.price_usd > 0);
    }

    // Sorting
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case "popular":
          return b.downloads_count - a.downloads_count;
        case "rating":
          return b.rating - a.rating;
        case "newest":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "price-low":
          return a.price_usd - b.price_usd;
        case "price-high":
          return b.price_usd - a.price_usd;
        default:
          return 0;
      }
    });

    setFilteredTemplates(filtered);
  };

  const installTemplate = async (template: WorkflowTemplate) => {
    try {
      // For paid templates, would integrate payment flow here
      if (template.price_usd > 0) {
        toast.info("Payment integration coming soon!");
        return;
      }

      // Simulate installation
      toast.success(`Installing "${template.name}"...`);
      
      // In real implementation, would download template and redirect to workflow builder
      setTimeout(() => {
        toast.success("Template installed successfully!");
      }, 2000);
    } catch (error) {
      toast.error("Failed to install template");
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < Math.floor(rating)
            ? "fill-yellow-400 text-yellow-400"
            : "text-gray-300"
        }`}
      />
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Header */}
      <div className="border-b border-gray-700 bg-gray-800/50 backdrop-blur-xl sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Package className="h-8 w-8 text-purple-400" />
              <div>
                <h1 className="text-2xl font-bold">Workflow Marketplace</h1>
                <p className="text-sm text-gray-400">Discover and share powerful AI workflows</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Button variant="outline" className="border-gray-600">
                <Upload className="h-4 w-4 mr-2" />
                Publish Template
              </Button>
              <Link href="/workflow">
                <Button className="bg-purple-600 hover:bg-purple-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Workflow
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            {/* Categories */}
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Categories
              </h3>
              <div className="space-y-1">
                {categories.map((category) => {
                  const Icon = category.icon;
                  const count = category.name === "All" 
                    ? templates.length 
                    : templates.filter(t => t.category === category.name).length;
                  
                  return (
                    <button
                      key={category.name}
                      onClick={() => setSelectedCategory(category.name)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${
                        selectedCategory === category.name
                          ? "bg-purple-600/20 text-purple-400"
                          : "hover:bg-gray-800 text-gray-300"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        <span className="text-sm">{category.name}</span>
                      </div>
                      <span className="text-xs text-gray-500">{count}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Filters */}
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Price
              </h3>
              <div className="space-y-2">
                {["all", "free", "paid"].map((filter) => (
                  <label key={filter} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="price"
                      value={filter}
                      checked={priceFilter === filter}
                      onChange={(e) => setPriceFilter(e.target.value)}
                      className="text-purple-600"
                    />
                    <span className="text-sm text-gray-300 capitalize">{filter}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Sort */}
            <div>
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Sort By
              </h3>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="popular">Most Popular</option>
                <option value="rating">Highest Rated</option>
                <option value="newest">Newest First</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
              </select>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Stats Bar */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center gap-3">
                  <Package className="h-8 w-8 text-purple-400" />
                  <div>
                    <p className="text-2xl font-bold">{templates.length}</p>
                    <p className="text-sm text-gray-400">Total Templates</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center gap-3">
                  <Download className="h-8 w-8 text-green-400" />
                  <div>
                    <p className="text-2xl font-bold">
                      {templates.reduce((sum, t) => sum + t.downloads_count, 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-400">Total Downloads</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center gap-3">
                  <Star className="h-8 w-8 text-yellow-400" />
                  <div>
                    <p className="text-2xl font-bold">
                      {(templates.reduce((sum, t) => sum + t.rating, 0) / templates.length).toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-400">Average Rating</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center gap-3">
                  <Users className="h-8 w-8 text-blue-400" />
                  <div>
                    <p className="text-2xl font-bold">
                      {new Set(templates.map(t => t.author.id)).size}
                    </p>
                    <p className="text-sm text-gray-400">Contributors</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Templates Grid */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
              </div>
            ) : filteredTemplates.length === 0 ? (
              <div className="text-center py-12">
                <Package className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No templates found matching your criteria</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence>
                  {filteredTemplates.map((template, index) => {
                    const Icon = categoryIcons[template.category] || Package;
                    
                    return (
                      <motion.div
                        key={template.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ delay: index * 0.05 }}
                        className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-purple-500 transition-all group"
                      >
                        {/* Preview Image or Icon */}
                        <div className="h-48 bg-gradient-to-br from-purple-600/20 to-pink-600/20 flex items-center justify-center relative">
                          <Icon className="h-24 w-24 text-white/20" />
                          
                          {/* Favorite Button */}
                          <button
                            onClick={() => toggleFavorite(template.id)}
                            className="absolute top-4 right-4 p-2 rounded-full bg-gray-900/50 backdrop-blur hover:bg-gray-900/80 transition-colors"
                          >
                            <Heart
                              className={`h-5 w-5 ${
                                favorites.has(template.id)
                                  ? "fill-red-500 text-red-500"
                                  : "text-gray-400"
                              }`}
                            />
                          </button>
                          
                          {/* Price Badge */}
                          {template.price_usd > 0 ? (
                            <div className="absolute top-4 left-4 px-3 py-1 bg-green-600 rounded-full text-sm font-semibold">
                              ${template.price_usd}
                            </div>
                          ) : (
                            <div className="absolute top-4 left-4 px-3 py-1 bg-purple-600 rounded-full text-sm font-semibold">
                              FREE
                            </div>
                          )}
                        </div>
                        
                        {/* Content */}
                        <div className="p-6">
                          <h3 className="text-xl font-semibold mb-2 group-hover:text-purple-400 transition-colors">
                            {template.name}
                          </h3>
                          
                          <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                            {template.description}
                          </p>
                          
                          {/* Author */}
                          <div className="flex items-center gap-2 mb-4">
                            <div className="h-6 w-6 rounded-full bg-gray-600" />
                            <span className="text-sm text-gray-400">
                              by {template.author.username}
                            </span>
                          </div>
                          
                          {/* Stats */}
                          <div className="flex items-center justify-between mb-4 text-sm">
                            <div className="flex items-center gap-1">
                              {renderStars(template.rating)}
                              <span className="text-gray-400 ml-1">
                                ({template.rating_count})
                              </span>
                            </div>
                            
                            <div className="flex items-center gap-3 text-gray-400">
                              <div className="flex items-center gap-1">
                                <Download className="h-4 w-4" />
                                <span>{template.downloads_count}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Clock className="h-4 w-4" />
                                <span>{template.estimated_run_time}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Tags */}
                          <div className="flex flex-wrap gap-2 mb-4">
                            {template.tags.slice(0, 3).map((tag) => (
                              <span
                                key={tag}
                                className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300"
                              >
                                {tag}
                              </span>
                            ))}
                            {template.tags.length > 3 && (
                              <span className="text-xs text-gray-500">
                                +{template.tags.length - 3} more
                              </span>
                            )}
                          </div>
                          
                          {/* Actions */}
                          <div className="flex gap-2">
                            <Button
                              onClick={() => installTemplate(template)}
                              className="flex-1 bg-purple-600 hover:bg-purple-700"
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Install
                            </Button>
                            <Button
                              variant="outline"
                              className="border-gray-600"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              className="border-gray-600"
                            >
                              <Share2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}