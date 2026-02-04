/// ==============================================================================
/// MODULE: Claim Submit Screen
/// ==============================================================================
///
/// Expense claim submission form for employees. Allows users to:
/// - Select claim category (e.g., Transport, Meals, Medical)
/// - Enter claim amount with validation against category max limits
/// - Attach receipt images via camera or gallery
/// - Submit claims for approval workflow
///
/// Uses [claimCategoriesProvider] to fetch available categories and their limits.
/// On successful submission, returns `true` to trigger list refresh.
/// ==============================================================================
library;

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/user_provider.dart';
import '../providers/chat_provider.dart';

final claimCategoriesProvider = FutureProvider<Map<String, dynamic>>((
  ref,
) async {
  final apiService = ref.read(apiServiceProvider);
  return await apiService.getClaimCategories();
});

class ClaimSubmitScreen extends ConsumerStatefulWidget {
  const ClaimSubmitScreen({super.key});

  @override
  ConsumerState<ClaimSubmitScreen> createState() => _ClaimSubmitScreenState();
}

class _ClaimSubmitScreenState extends ConsumerState<ClaimSubmitScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  String? _selectedCategoryId;
  String? _selectedCategoryName;
  double? _maxAmount;
  bool _isSubmitting = false;
  XFile? _receiptImage;

  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1200,
        maxHeight: 1200,
        imageQuality: 85,
      );
      if (image != null) {
        setState(() => _receiptImage = image);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Receipt for ${_selectedCategoryName ?? "claim"} selected! 📸',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error picking image: $e'),
          backgroundColor: Colors.redAccent,
        ),
      );
    }
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E1E1E),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt, color: Colors.orange),
                title: const Text('Take Photo'),
                subtitle: const Text('Use camera to capture receipt'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library, color: Colors.purple),
                title: const Text('Choose from Gallery'),
                subtitle: const Text('Select from your photos'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImage(ImageSource.gallery);
                },
              ),
              if (_receiptImage != null)
                ListTile(
                  leading: const Icon(Icons.delete, color: Colors.redAccent),
                  title: const Text('Remove Image'),
                  onTap: () {
                    Navigator.pop(ctx);
                    setState(() => _receiptImage = null);
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _submitClaim() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedCategoryId == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Please select a category')));
      return;
    }

    final amount = double.tryParse(_amountController.text.trim());
    if (amount == null || amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid amount')),
      );
      return;
    }

    if (_maxAmount != null && amount > _maxAmount!) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Amount exceeds maximum limit of RM${_maxAmount!.toStringAsFixed(2)}',
          ),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final userId = ref.read(userProvider).userId!;
      final apiService = ref.read(apiServiceProvider);

      final result = await apiService.submitClaim(
        userId: userId,
        categoryId: _selectedCategoryId!,
        amount: amount,
        description: _descriptionController.text.trim().isNotEmpty
            ? _descriptionController.text.trim()
            : null,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? 'Claim submitted! 💰'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final categoriesAsync = ref.watch(claimCategoriesProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(
          "Submit Claim",
          style: GoogleFonts.playfairDisplay(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ShadCard(
                width: double.infinity,
                backgroundColor: Colors.white10,
                border: ShadBorder.all(color: Colors.white24, width: 1),
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Icon(
                      Icons.receipt_long,
                      color: Colors.white,
                      size: 40,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Expense Claim",
                            style: GoogleFonts.playfairDisplay(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            "Get reimbursed for work expenses",
                            style: GoogleFonts.inter(color: Colors.grey[400]),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn().slideY(begin: 0.2, end: 0),

              const SizedBox(height: 24),

              Text(
                "Category *",
                style: TextStyle(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              categoriesAsync.when(
                data: (data) {
                  final categories = (data['data'] as List?) ?? [];
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    decoration: BoxDecoration(
                      color: Colors.white10,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white24),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedCategoryId,
                        hint: const Text(
                          "Select category",
                          style: TextStyle(color: Colors.grey),
                        ),
                        isExpanded: true,
                        dropdownColor: Colors.black,
                        items: categories.map<DropdownMenuItem<String>>((c) {
                          final maxAmt = c['max_amount'];
                          final name = c['name'] ?? 'Unknown';
                          final suffix = maxAmt != null
                              ? ' (Max: RM$maxAmt)'
                              : '';
                          return DropdownMenuItem(
                            value: c['id'].toString(),
                            child: Text(
                              '$name$suffix',
                              style: const TextStyle(color: Colors.white),
                            ),
                          );
                        }).toList(),
                        onChanged: (value) {
                          final cat = categories.firstWhere(
                            (c) => c['id'].toString() == value,
                            orElse: () => {},
                          );
                          setState(() {
                            _selectedCategoryId = value;
                            _selectedCategoryName = cat['name'];
                            _maxAmount = cat['max_amount']?.toDouble();
                          });
                        },
                      ),
                    ),
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Text(
                  'Failed to load: $e',
                  style: const TextStyle(color: Colors.redAccent),
                ),
              ),

              if (_maxAmount != null)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        size: 14,
                        color: Colors.grey[500],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Maximum claimable: RM${_maxAmount!.toStringAsFixed(2)}',
                        style: TextStyle(color: Colors.grey[500], fontSize: 12),
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 20),

              Text(
                "Amount (RM) *",
                style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              ShadInput(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                placeholder: const Text("0.00"),
                leading: const Padding(
                  padding: EdgeInsets.all(12.0),
                  child: Text(
                    "RM",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ).animate().fadeIn(delay: 100.ms),

              const SizedBox(height: 20),

              Text(
                "Description *",
                style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 14),
              ),
              const SizedBox(height: 8),
              ShadInput(
                controller: _descriptionController,
                maxLines: 3,
                placeholder: const Text(
                  "e.g., Parking at KLCC, Grab to client meeting...",
                ),
              ).animate().fadeIn(delay: 200.ms),

              const SizedBox(height: 20),

              _buildReceiptSection(),

              const SizedBox(height: 32),

              ShadButton(
                width: double.infinity,
                onPressed: _isSubmitting ? null : _submitClaim,
                child: _isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.black,
                        ),
                      )
                    : Text(
                        "Submit Claim",
                        style: GoogleFonts.inter(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
              ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2, end: 0),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReceiptSection() {
    if (_receiptImage != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Receipt Image",
            style: TextStyle(color: Colors.grey[400], fontSize: 14),
          ),
          const SizedBox(height: 8),
          Stack(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(
                  File(_receiptImage!.path),
                  height: 200,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
              Positioned(
                top: 8,
                right: 8,
                child: Row(
                  children: [
                    _buildImageActionButton(
                      icon: Icons.refresh,
                      color: Colors.blue,
                      onTap: _showImageSourceDialog,
                    ),
                    const SizedBox(width: 8),
                    _buildImageActionButton(
                      icon: Icons.close,
                      color: Colors.redAccent,
                      onTap: () => setState(() => _receiptImage = null),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.check_circle, size: 14, color: Colors.green[400]),
              const SizedBox(width: 6),
              Text(
                'Image ready to upload',
                style: TextStyle(color: Colors.green[400], fontSize: 12),
              ),
            ],
          ),
        ],
      );
    }

    return InkWell(
      onTap: _showImageSourceDialog,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white10,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white24, style: BorderStyle.solid),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white10,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.add_a_photo,
                color: Colors.white,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Upload Receipt",
                    style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Take photo or choose from gallery",
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  Widget _buildImageActionButton({
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.7),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
    );
  }
}
